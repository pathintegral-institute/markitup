from typing import BinaryIO, Any
import pymupdf4llm

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config
from ._html_converter import HtmlConverter
import fitz


class PdfConverter(DocumentConverter):
    """
    Converts PDFs to Markdown with embedded images.
    """

    def __init__(self, config: Config):
        self.config = config

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Create a document object from the stream
        doc = fitz.open(stream=file_stream, filetype="pdf")

        md_content = pymupdf4llm.to_markdown(doc, 
                                        ignore_graphics=True,
                                        table_strategy='lines',
                                        extract_words=True,
                                        embed_images=True,
                                        page_chunks=True)
    
        llm_msgs = DocumentConverterResult(
            markdown=md_content,
            config=self.config,
            # stream_info=stream_info,
        ).to_llm()
        
        to_chunkfy_string = '\n'.join([msg['content'] for msg in llm_msgs if msg['type'] == "text"])
