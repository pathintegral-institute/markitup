from typing import BinaryIO, Any
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config
import base64


class ImageConverter(DocumentConverter):
    """
    Converts image files to markdown with embedded base64 image.
    """

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Read the image data
        image_bytes = file_stream.read()

        # Determine image extension from magic_type
        image_ext = "png"  # Default extension
        match stream_info.magic_type:
            case "image/jpeg" | "image/jpg":
                image_ext = "jpeg"
            case "image/png":
                image_ext = "png"
            case "image/webp":
                image_ext = "webp"

        if 'image' in self.config.modalities:
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Create markdown with embedded image
            markdown_content = f"![Image](data:image/{image_ext};base64,{img_base64})\n\n"

            return DocumentConverterResult(
                markdown=markdown_content,
                config=self.config,
            )
        else:
            return DocumentConverterResult(
                markdown="No Image read as the supported modalities do not include 'image'",
                config=self.config,
            )