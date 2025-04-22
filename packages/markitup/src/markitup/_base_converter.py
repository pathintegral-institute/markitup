import os
import tempfile
from warnings import warn
from typing import Any, Union, BinaryIO, Optional, List, Dict
from ._schemas import StreamInfo
import re
import base64


class DocumentConverterResult:
    """The result of converting a document to Markdown."""

    def __init__(
        self,
        markdown: str = "",
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
        - title: Optional title of the document.
        """
        self.markdown = markdown
        self.audio_stream = audio_stream
        self.title = title
        self.stream_info = stream_info

    def to_llm(self) -> List[Dict[str, Any]]:
        """
        Convert markdown with base64 images to a format compatible with OpenAI's API.

        This function parses the markdown content, extracting text and images in their
        original order, and returns a list of content elements in OpenAI's format.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the content elements
                                (text and images) in their original order.
        """

        # Pattern to match markdown image syntax with base64 data
        pattern = r'!\[(.*?)\]\(data:(.*?);base64,(.*?)\)'

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

            # Add the image
            content.append({
                "type": "image",
                "image_url": {
                    "url": f"data:{content_type};base64,{b64_data}"
                },
                "alt_text": alt_text
            })

            last_end = match.end()

        # Add any remaining text after the last image
        if last_end < len(self.markdown):
            text_chunk = self.markdown[last_end:].strip()
            if text_chunk:
                content.append({
                    "type": "text",
                    "text": text_chunk
                })
        if self.audio_stream:
            audio_b64 = base64.b64encode(
                self.audio_stream.read()).decode('utf-8')
            content.append({
                "type": "media",
                "mime_type": self.stream_info.magic_type,
                "data": audio_b64
            })
        return content

    @property
    def text_content(self) -> str:
        """Soft-deprecated alias for `markdown`. New code should migrate to using `markdown` or __str__."""
        return self.markdown

    @text_content.setter
    def text_content(self, markdown: str):
        """Soft-deprecated alias for `markdown`. New code should migrate to using `markdown` or __str__."""
        self.markdown = markdown

    def __str__(self) -> str:
        """Return the converted Markdown text."""
        return self.markdown


class DocumentConverter:
    """Abstract superclass of all DocumentConverters."""

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
