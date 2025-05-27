import os
import tempfile
from warnings import warn
from typing import Any, Union, BinaryIO, Optional, List, Dict
from ._schemas import StreamInfo, Config, MarkdownChunk, Chunk
import re
import base64
from PIL import Image
from io import BytesIO
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentConverterResult:
    """The result of converting a document to Markdown."""

    def __init__(
        self,
        markdown: str = "",
        markdown_chunk_list: Optional[List[MarkdownChunk]] = None,
        config: Optional[Config] = None,
        *,
        title: Optional[str] = None,
        audio_stream: Optional[BinaryIO] = None,
        stream_info: Optional[StreamInfo] = None,
    ):
        """
        Initialize the DocumentConverterResult.

        The only required parameter is the converted Markdown text.
        The title, and any other metadata that may be added in the future, are optional.

        Parameters:
        - markdown: The converted Markdown text.
        - config: Optional configuration settings.
        - title: Optional title of the document.
        - audio_stream: Optional audio data.
        - stream_info: Optional stream information.
        """
        self.markdown = markdown
        self.markdown_chunk_list = markdown_chunk_list
        self.audio_stream = audio_stream
        self.title = title
        self.stream_info = stream_info
        self.config = config

    def to_llm(self) -> List[Dict[str, Any]]:
        """
        Convert markdown with base64 images to a format compatible with OpenAI's API.

        This function parses the markdown content, extracting text and images in their
        original order, and returns a list of content elements in OpenAI's format.

        If chunking is enabled in the config, it processes the markdown_chunk_list instead
        of the full markdown, preserving chunk metadata.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the content elements
                                (text and images) in their original order.
        """
        # Check if chunking is enabled and markdown_chunk_list is available
        if self.config and self.config.chunk:
            if not self.markdown_chunk_list:
                self.markdown_chunk_list = self._gen_markdown_chunk_list_from_md_content()
            return self._process_chunked_content()
        else:
            return self._process_full_markdown()

    def _gen_markdown_chunk_list_from_md_content(self) -> List[MarkdownChunk]:
        llm_dict_list = self._process_full_markdown()
        chunks = []
        chunk_id = 0
        _chunker = RecursiveCharacterTextSplitter(
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
        for item in llm_dict_list:
            if item['type'] == "text":
                # chunk the text parts
                md_content = item['text']
                text_content_list = _chunker.split_text(md_content)
                for text_content in text_content_list:
                    text_chunk = Chunk(
                        chunk_modality="text",
                        chunk_id=chunk_id,
                        content={
                            "type": "text",
                            "text": text_content
                        },
                    )
                    chunk_id += 1
                    chunks.append(text_chunk)
            else:
                # Then it is image, we just form the chunk
                image_chunk = Chunk(
                    chunk_modality="image",
                    chunk_id=chunk_id,
                    content=item,
                )
                chunk_id += 1
                chunks.append(image_chunk)
        return chunks

    def _process_chunked_content(self) -> List[Chunk]:
        """
        Process content when chunking is enabled.

        Returns:
            List[Chunk]: A list of Chunk objects with appropriate metadata.
        """
        chunks = []

        for markdown_chunk in self.markdown_chunk_list:
            if markdown_chunk.chunk_modality == "text":
                # Create text chunk
                text_content = {
                    "type": "text",
                    "text": markdown_chunk.content
                }

                # Create Chunk object for text
                text_chunk = Chunk(
                    chunk_modality="text",
                    chunk_id=markdown_chunk.chunk_id,
                    content=text_content,
                    page_id=markdown_chunk.page_id,
                    bbox_list=markdown_chunk.bbox_list
                )
                chunks.append(text_chunk)

            elif markdown_chunk.chunk_modality == "image":
                # For other than pdf, the image_dict here is already present, no need to match
                if isinstance(markdown_chunk.content, dict):
                    image_chunk = Chunk(
                        chunk_modality="image",
                        chunk_id=markdown_chunk.chunk_id,
                        content=markdown_chunk.content,
                        page_id=markdown_chunk.page_id,
                        bbox_list=markdown_chunk.bbox_list
                    )
                    chunks.append(image_chunk)
                else:
                    # Pattern to match markdown image syntax with base64 data
                    pattern = r'!\[(.*?)\]\(data:(.*?);base64,(.*?)\s*\)'

                    # Process image chunk
                    match = re.search(pattern, markdown_chunk.content)
                    if match:
                        alt_text, content_type, b64_data = match.groups()

                        # Decode base64 data
                        img_data = base64.b64decode(b64_data)

                        # Process image and get formatted result
                        image_dict = self._process_image(img_data, content_type)

                        # Create Chunk object for image
                        image_chunk = Chunk(
                            chunk_modality="image",
                            chunk_id=markdown_chunk.chunk_id,
                            content=image_dict,
                            page_id=markdown_chunk.page_id,
                            bbox_list=markdown_chunk.bbox_list
                        )
                        chunks.append(image_chunk)

        return chunks

    def _process_full_markdown(self) -> List[Dict[str, Any]]:
        """
        Process the full markdown when chunking is disabled.

        Returns:
            List[Dict[str, Any]]: A list of content elements.
        """
        # Pattern to match markdown image syntax with base64 data
        pattern = r'!\[(.*?)\]\(data:(.*?);base64,(.*?)\s*\)'

        content = []
        last_end = 0

        # Process the document sequentially to maintain order
        for match in re.finditer(pattern, self.markdown):
            # Add the text before this image if any
            if match.start() > last_end:
                text_chunk = self.markdown[last_end:match.start()].strip()
                if text_chunk:
                    content.append({
                        "type": "text",
                        "text": text_chunk
                    })

            # Extract image data
            alt_text, content_type, b64_data = match.groups()

            # Decode base64 data
            img_data = base64.b64decode(b64_data)

            # Process image and get formatted result
            image_dict = self._process_image(img_data, content_type)
            content.append(image_dict)

            last_end = match.end()

        # Add any remaining text after the last image
        if last_end < len(self.markdown):
            text_chunk = self.markdown[last_end:].strip()
            if text_chunk:
                content.append({
                    "type": "text",
                    "text": text_chunk
                })

        # Add audio if present
        if self.audio_stream:
            audio_b64 = base64.b64encode(
                self.audio_stream.read()).decode('utf-8')
            content.append({
                "type": "media",
                "mime_type": self.stream_info.magic_type,
                "data": audio_b64
            })

        return content

    def _process_image(self, image_data: bytes, content_type: str) -> Dict[str, Any]:
        """
        Process image data according to configuration settings and return a formatted dictionary.

        This function handles:
        1. Resizing images to stay within max_width_or_height if specified
        2. Converting to WebP format if image_use_webp is enabled
        3. Formatting the result as a dictionary ready for the API

        Parameters:
        - image_data: The original image data as bytes
        - content_type: The original mime type of the image
        - metadata: Optional metadata to include in the response
        - quality: The quality setting (0-100) for WebP conversion

        Returns:
        - Dict[str, Any]: Formatted dictionary with processed image data
        """
        img = Image.open(BytesIO(image_data))
        original_width, original_height = img.size

        # Resize if needed based on config
        if hasattr(self.config, "image_max_width_or_height") and self.config.image_max_width_or_height > 0:
            max_size = self.config.image_max_width_or_height

            # Calculate resize ratio if either dimension exceeds max size
            if original_width > max_size or original_height > max_size:
                ratio = min(max_size / original_width,
                            max_size / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)

        # Process according to config
        if self.config.image_use_webp:
            # Convert to WebP
            processed_data = self._convert_image_to_webp(img, quality=80)
            content_type = "image/webp"

        # Convert to base64
        b64_data = base64.b64encode(processed_data).decode('utf-8')

        # Construct the result dictionary in OpenAI format
        result = {
            "type": "image_url",
            "image_url": {
                "url": f"data:{content_type};base64,{b64_data}"
            }
        }

        return result

    def _convert_image_to_webp(self, img, quality: int = 80) -> bytes:
        """
        Convert a PIL Image to WebP format.

        Parameters:
        - img: A PIL Image object
        - quality: The quality setting (0-100) for WebP conversion.

        Returns:
        - WebP converted image data as bytes.
        """
        # Convert to RGB if image has alpha channel or is not in RGB mode
        if img.mode in ('RGBA', 'LA') or (img.mode != 'RGB' and img.mode != 'L'):
            img = img.convert('RGB')

        # Save as WebP to a BytesIO object
        webp_buffer = BytesIO()
        img.save(webp_buffer, format="WEBP", quality=quality)
        webp_buffer.seek(0)
        return webp_buffer.read()

    def __str__(self) -> str:
        """Return the converted Markdown text."""
        return self.markdown


class DocumentConverter:
    """Abstract superclass of all DocumentConverters."""

    def __init__(self, config: Config):
        self.config = config

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        ** kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        """
        Convert a document to Markdown text.

        Prameters:
        - file_stream: The file-like object to convert. Must support seek(), tell(), and read() methods.
        - stream_info: The StreamInfo object containing metadata about the file (mimetype, extension, charset, set)
        - kwargs: Additional keyword arguments for the converter.

        Returns:
        - DocumentConverterResult: The result of the conversion, which includes the title and markdown content.

        Raises:
        - FileConversionException: If the mimetype is recognized, but the conversion fails for some other reason.
        - MissingDependencyException: If the converter requires a dependency that is not installed.
        """
        raise NotImplementedError("Subclasses must implement this method")
