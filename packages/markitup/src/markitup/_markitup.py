from typing import Any, List, Dict, Optional, Union, BinaryIO
from pathlib import Path
from urllib.parse import urlparse
from warnings import warn
import magic
import mimetypes
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
        plugins: Optional[Dict[str, DocumentConverter]] = None,
    ):
        self.config = config
        self.accepted_categories = ["text", "image", "audio", "pdf", "docx", "pptx", "xlsx", "xls", "csv", "html"]
        self.converters = {
            "text": PlainTextConverter,
            "image": ImageConverter,
            "audio": AudioConverter,
            "pdf": PdfConverter,
            "docx": DocxConverter,
            "pptx": PptxConverter,
            "xlsx": XlsxConverter,
            "xls": XlsConverter,
            "csv": CsvConverter,
            "html": HtmlConverter,
        }
        if plugins:
            for plugin_name, converter in plugins.items():
                self.converters[plugin_name] = converter
        
    def convert(self, stream: BinaryIO, file_name: str, **kwargs) -> Dict[DocumentConverterResult, StreamInfo]:
        stream_info: StreamInfo = self._get_stream_info(stream, file_name)
        # Deal with unsupported file types
        try:
            if stream_info.category in self.converters.keys():
                converter = self.converters[stream_info.category](config=self.config)
                return converter.convert(stream, stream_info, **kwargs), stream_info
            else:
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

    def _get_stream_info(self, byte_stream: BinaryIO, filename: str) -> StreamInfo:
        byte_stream.seek(0)

        # Get file content for analysis
        file_content = byte_stream.read()

        # Use python-magic to determine file type based on content
        magic_type = magic.from_buffer(file_content, mime=True)
        if magic_type == "application/octet-stream":
            guessed_type, _ = mimetypes.guess_type(filename)
            if guessed_type:
                magic_type = guessed_type

        # Determine file category based on magic_type
        if magic_type.startswith("image/"):
            if magic_type in ["image/webp", "image/jpeg", "image/png", "image/jpg"]:
                category = "image"
            else:
                category = "other"
        elif magic_type ==("audio/mpeg"):
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
            elif magic_type == "text/html":
                category = "html"
            else:
                category = "text"
        else:
            category = "other"

        byte_stream.seek(0)
        return StreamInfo(magic_type=magic_type, category=category)
