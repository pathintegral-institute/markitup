from typing import BinaryIO, Any, Tuple, List, Dict
from IPython.core.display import Markdown
import pymupdf4llm
from collections import Counter
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config, MarkdownChunk
from ._html_converter import HtmlConverter
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
import base64
import logging
logger = logging.getLogger(__name__)


class PdfConverter(DocumentConverter):
    """
    Converts PDFs to Markdown with embedded images.
    """
    def __init__(self, config: Config):
        super().__init__(config=config)
        self._chunker = RecursiveCharacterTextSplitter(
            separators=[
                "\n#{1,6} ",  # Headers (H1 through H6)
                "```\n",      # Code blocks
                "\n\\*\\*\\*+\n",  # Horizontal lines (*)
                "\n\n",       # Double new lines
                "\n",         # New line
                " ",          # Spaces
                "",           # Character
            ],
            keep_separator=True,
            is_separator_regex=True,  # Enable regex for complex separators
        ).from_tiktoken_encoder(
            model_name=self.config.tiktoken_encoder,
            chunk_size=self.config.chunk_size,
            chunk_overlap=0,
        )

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Create a document object from the stream
        doc = fitz.open(stream=file_stream, filetype="pdf")

        if not self.config.chunk:
            md_content = pymupdf4llm.to_markdown(
                doc,
                ignore_graphics=True,
                table_strategy='lines',
                embed_images=bool('image' in self.config.modalities),
                page_chunks=False)
            return DocumentConverterResult(
                markdown=md_content,
                config=self.config,
                stream_info=stream_info,
            )
        
        pdf_dict_list = pymupdf4llm.to_markdown(
            doc,
            ignore_graphics=True,
            table_strategy='lines',
            extract_words=True,
            embed_images=False,
            page_chunks=True)
        
        final_chunk_list = []
        for idx, pdf_dict in enumerate(pdf_dict_list):
            md_content = pdf_dict['text']
            words_tuple_list = pdf_dict['words']

            text_chunk_list = self._chunker.split_text(md_content)
            categorical_list = create_categorical_mapping(text_chunk_list, words_tuple_list= words_tuple_list)
            block_categories = determine_block_categories(words_tuple_list, categorical_list)
            text_tuple_list = []
            all_blocks_tuple_list = doc[idx].get_text('dict')
            for block_tuple in all_blocks_tuple_list['blocks']:
                if 'lines' in block_tuple:
                    text_tuple_list.append(block_tuple)
            # TEXT CHUNK
            text_chunk_list = [MarkdownChunk(chunk_modality='text', content=chunk_str, chunk_id=0, page_id=idx) for chunk_str in text_chunk_list]
            for key in block_categories:
                chunk_id = block_categories[key]
                selected_tuple = text_tuple_list[key]
                text_chunk_list[chunk_id].bbox_id_list.append(int(selected_tuple['number']))
                text_chunk_list[chunk_id].bbox_list.append(selected_tuple['bbox'])
            
            # IMAGE CHUNK
            image_chunk_list = []
            for image in pdf_dict['images']:
                image_md_chunk = image_dict_to_chunk(
                    image_dict=all_blocks_tuple_list['blocks'][image['number']], page_id=idx
                )
                if image_md_chunk:
                    image_chunk_list.append(image_md_chunk)
            page_chunk_list = sort_chunks_based_on_bbox_id(
                unsorted_chunks=text_chunk_list+image_chunk_list,
                offset=len(final_chunk_list))
            final_chunk_list.extend(page_chunk_list)
        
        return DocumentConverterResult(
            markdown_chunk_list=final_chunk_list,
            config=self.config,
            stream_info=stream_info,
        )


def image_dict_to_chunk(image_dict: Dict[str, Any], page_id: int) -> MarkdownChunk:
    """
    Convert an image dictionary to a Chunk with markdown inline image content.
    
    Args:
        image_dict: Dictionary containing image data and metadata from the PDF parser
    
    Returns:
        Chunk: A Chunk object with the image content and metadata
    """
    # Extract the image data
    image_data = image_dict.get('image', b'')

    if image_data:
        base64_str = base64.b64encode(image_data).decode('utf-8')
        # Create a markdown image with base64 data
        # We determine image format from the 'ext' field, defaulting to jpeg
        img_format = image_dict.get('ext', 'jpeg')
        markdown_content = f"![Image](data:image/{img_format};base64,{base64_str})"
    else:
        # Fallback if no image data is available
        markdown_content = "![Image not available]()"
    
    try:
        return MarkdownChunk(
            chunk_modality='image',
            content=markdown_content,
            chunk_id=0,
            page_id=page_id,
            bbox_id_list=[int(image_dict['number'])],
            bbox_list=[image_dict['bbox']]
        )
    except Exception as e:
        logger.error(f"Failed to convert image dictionary to chunk: {e}")
        return None


def create_categorical_mapping(chunk_list: list[str],
                               words_tuple_list: list[Tuple[float, float, float, float, str, int, int, int]]) ->List[int]:
    """
    Create a mapping between text chunks and word positions that preserves proportional distribution.
    
    This function takes text chunks and maps them to individual word positions in words_tuple_list,
    ensuring each chunk occupies a proportional amount of space relative to its word count.
    
    Args:
        chunk_list: List of text chunks (strings) to be mapped
        words_tuple_list: List of word tuples representing the target word sequence
    
    Returns:
        List of chunk indices (same length as words_tuple_list)
        where each position contains the index of the chunk that covers that word
    
    Example:
        >>> chunk_list = ["Hello world", "This is a test"]
        >>> words_tuple_list = [("Hello",), ("world",), ("This",), ("is",), ("a",), ("test",)]
        >>> categorical_list = create_categorical_mapping(chunk_list, words_tuple_list)
        >>> categorical_list
        [0, 0, 1, 1, 1, 1]  # First two words map to chunk 0, rest to chunk 1
        The function also works for cases where the number do not match by linear approximation
    
    Note:
        The function guarantees that len(categorical_list) == len(words_tuple_list)
        by using proportional scaling with rounding adjustments.
    """
    # Split text to chunks and calculate sizes
    cumulative_chunk_word_count = []
    for idx, chunk in enumerate(chunk_list):
        if not cumulative_chunk_word_count:
            cumulative_chunk_word_count.append(len(chunk.split()))
        else:
            cumulative_chunk_word_count.append(len(chunk.split())+cumulative_chunk_word_count[idx-1])
    
    # Calculate bbox word count
    bbox_word_count = len(words_tuple_list)
    
    # Calculate scale factor
    scale_factor = bbox_word_count / cumulative_chunk_word_count[-1]
    
    # Create categorical list
    categorical_list = []
    for idx, cumulative_cwc in enumerate(cumulative_chunk_word_count):
        categorical_list += int(round(scale_factor * cumulative_cwc) - len(categorical_list)) * [idx]
    
    return categorical_list


def determine_block_categories(words_tuple_list: List[Tuple[float, float, float, float, str, int, int, int]],
                               categorical_list: List[int]) -> Dict[int, int]:
    """
    Determine the category for each block based on majority voting from words in that block.
    
    Args:
        words_tuple_list: List of word tuples (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        categorical_list: List of categories (same length as words_tuple_list)
    
    Returns:
        Dictionary mapping block_no to its majority category
    """
    # Create a mapping of block_no to list of categories from words in that block
    block_to_categories = {}
    
    # Iterate through words and their categories
    for i, word_tuple in enumerate(words_tuple_list):
        # Extract block_no from word tuple (index 5)
        block_no = word_tuple[5]
        category = categorical_list[i]
        
        if block_no not in block_to_categories:
            block_to_categories[block_no] = []
        
        block_to_categories[block_no].append(category)
    
    # Determine majority category for each block
    block_categories = {}
    
    for block_no, categories in block_to_categories.items():
        # Count occurrences of each category
        category_counts = Counter(categories)
        
        # Get the category with the highest count (majority)
        majority_category = category_counts.most_common(1)[0][0]
        
        block_categories[block_no] = majority_category
    
    return block_categories


def sort_chunks_based_on_bbox_id(unsorted_chunks: List[MarkdownChunk], offset: int = 0) -> List[MarkdownChunk]:
    # First, sort chunks based on their minimum bbox_id
    # For chunks without bbox_id_list, we'll place them at the end
    def get_min_bbox_id(chunk: MarkdownChunk) -> int:
        if chunk.bbox_id_list and len(chunk.bbox_id_list) > 0:
            return min(chunk.bbox_id_list)
        return float('inf')  # Place chunks without bbox_id_list at the end

    # Sort the chunks based on the minimum bbox_id
    sorted_chunks = sorted(unsorted_chunks, key=get_min_bbox_id)

    # Reassign chunk_ids to maintain sequential ordering
    for i, chunk in enumerate(sorted_chunks):
        chunk.chunk_id = i + offset

    return sorted_chunks