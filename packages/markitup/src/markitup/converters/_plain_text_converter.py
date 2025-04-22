from typing import BinaryIO, Any
from charset_normalizer import from_bytes
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo


class PlainTextConverter(DocumentConverter):
    """Anything with content type text/plain"""
    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        text_content = str(from_bytes(file_stream.read()).best())
        return DocumentConverterResult(markdown=text_content)
