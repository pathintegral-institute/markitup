import sys

from typing import BinaryIO, Any

from ._html_converter import HtmlConverter
from ..converter_utils.docx.pre_process import pre_process_docx
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config
import mammoth


class DocxConverter(HtmlConverter):
    """
    Converts DOCX files to Markdown. Style information (e.g.m headings) and tables are preserved where possible.
    """

    def __init__(self, config: Config):
        super().__init__(config=config)
        self._html_converter = HtmlConverter(config=config)

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:

        style_map = kwargs.get("style_map", None)
        pre_process_stream = pre_process_docx(file_stream)
        return self._html_converter.convert_string(
            mammoth.convert_to_html(
                pre_process_stream, style_map=style_map).value,
            **kwargs,
        )
