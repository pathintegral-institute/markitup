from typing import BinaryIO, Any
import io
import base64

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
        self._html_converter = HtmlConverter(config=config)

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Create a document object from the stream
        doc = fitz.open(stream=file_stream, filetype="pdf")

        # Extract text and images from all pages
        markdown_content = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Get text with the default "text" mode which gives plain text
            page_text = page.get_text("html")
            # Add page marker
            markdown_content += f"\n\n## Page {page_num + 1}\n\n"
            html_conterted_md = self._html_converter.convert_string(page_text)
            markdown_content += html_conterted_md.markdown
            markdown_content += "\n\n"
        # Close the document to free resources
        doc.close()
        return DocumentConverterResult(
            markdown=markdown_content,
            config=self.config,
        )
