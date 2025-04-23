from typing import Any, List, Dict, Optional, Union, BinaryIO
from pathlib import Path
from urllib.parse import urlparse
from warnings import warn
import magic

from ._schemas import StreamInfo, Config

from .converters import (
    PlainTextConverter,
    HtmlConverter,
    ImageConverter,
    PdfConverter,
    DocxConverter,
    XlsxConverter,
    XlsConverter,
    PptxConverter,
    AudioConverter,
    CsvConverter,
)

from ._base_converter import DocumentConverter, DocumentConverterResult

from ._exceptions import (
    FileConversionException,
    UnsupportedFormatException,
    FailedConversionAttempt,
)


class MarkItUp:
    """(In preview) An extremely simple text-based document reader, suitable for LLM use.
    This reader will convert common file-types or webpages to Markdown."""

    def __init__(
        self,
        config: Config = Config(),
    ):
        self.config = config

    def convert(self, stream: BinaryIO) -> Dict[DocumentConverterResult, StreamInfo]:
        stream_info: StreamInfo = self._get_stream_info(stream)
        # Deal with unsupported file types
        try:
            match stream_info.category:
                case "text":
                    return PlainTextConverter().convert(stream, stream_info), stream_info
                case "pptx":
                    return PptxConverter(config=self.config).convert(stream, stream_info), stream_info
                case "pdf":
                    return PdfConverter(config=self.config).convert(stream, stream_info), stream_info
                case "audio":
                    return AudioConverter(config=self.config).convert(stream, stream_info), stream_info
                case "xlsx":
                    return XlsxConverter(config=self.config).convert(stream, stream_info), stream_info
                case "xls":
                    return XlsConverter(config=self.config).convert(stream, stream_info), stream_info
                case "csv":
                    return CsvConverter().convert(stream, stream_info), stream_info
                case "docx":
                    return DocxConverter(config=self.config).convert(stream, stream_info), stream_info
                case "image":
                    return ImageConverter(config=self.config).convert(stream, stream_info), stream_info
                case _:
                    match stream_info.category:
                        case "ppt":
                            raise UnsupportedFormatException(
                                ".ppt files are not supported, try .pptx instead")
                        case "doc":
                            raise UnsupportedFormatException(
                                ".doc files are not supported, try .docx instead")
                        case "other":
                            raise UnsupportedFormatException(
                                f"{stream_info.magic_type} files are not supported")
        except FailedConversionAttempt:
            raise FileConversionException(
                f"Failed to convert file of type {stream_info.magic_type}")

    def _get_stream_info(self, byte_stream: BinaryIO) -> StreamInfo:
        original_position = byte_stream.tell()

        # Reset stream position to beginning
        byte_stream.seek(0)

        # Get file content for analysis
        file_content = byte_stream.read()

        # Use python-magic to determine file type based on content
        magic_type = magic.from_buffer(file_content, mime=True)

        # Determine file category based on magic_type
        if magic_type.startswith("image/"):
            if magic_type in ["image/webp", "image/jpeg", "image/png", "image/jpg"]:
                category = "image"
            else:
                category = "other"
        elif magic_type.startswith("audio/"):
            category = "audio"
        elif magic_type.startswith("video/"):
            category = "video"
        elif magic_type.startswith("application/vnd.ms-excel"):
            category = 'xls'
        elif magic_type.startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
            category = "xlsx"
        elif magic_type.startswith("application/vnd.ms-powerpoint"):
            category = 'ppt'
        elif magic_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            category = "pptx"
        elif magic_type.startswith("application/msword"):
            category = 'doc'
        elif magic_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            category = "docx"
        elif magic_type == "application/pdf":
            category = "pdf"
        elif magic_type == "application/csv":
            category = "csv"
        elif magic_type.startswith("text/"):
            if magic_type == "text/csv":
                category = "csv"
            else:
                category = "text"
        else:
            category = "other"

        byte_stream.seek(original_position)
        return StreamInfo(magic_type=magic_type, category=category)
