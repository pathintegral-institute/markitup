from typing import BinaryIO, Any
from charset_normalizer import from_bytes
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config


class PlainTextConverter(DocumentConverter):
    """Anything with content type text/plain"""    
    def convert(self, file_stream: BinaryIO, stream_info: StreamInfo, **kwargs: Any) -> DocumentConverterResult:
        content = file_stream.read()
        text_content = str(from_bytes(content).best())
        
        return DocumentConverterResult(markdown=text_content)
