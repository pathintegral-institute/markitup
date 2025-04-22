from typing import BinaryIO, Any
import io
import base64

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo

import fitz


class PdfConverter(DocumentConverter):
    """
    Converts PDFs to Markdown with embedded images.
    """

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
        image_count = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Get text with the default "text" mode which gives plain text
            page_text = page.get_text("text")
            # Add page marker
            markdown_content += f"\n\n## Page {page_num + 1}\n\n"
            markdown_content += page_text + "\n\n"

            # Extract images from the page
            image_list = page.get_images(full=True)

            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]  # Get the image reference
                base_image = doc.extract_image(xref)

                if base_image:
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    try:
                        # Convert image to base64 for markdown embedding
                        img_base64 = base64.b64encode(
                            image_bytes).decode('utf-8')
                        # Add image to markdown with a unique identifier
                        image_count += 1
                        markdown_content += f"![Image {image_count}](data:image/{image_ext};base64,{img_base64})\n\n"
                    except Exception as e:
                        markdown_content += f"*[Error processing image {image_count}: {str(e)}]*\n\n"

        # Close the document to free resources
        doc.close()
        print(markdown_content)
        return DocumentConverterResult(
            markdown=markdown_content,
        )
