import io
from typing import Any, BinaryIO, Optional, Tuple

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config
from .._exceptions import MissingDependencyException
from ..converter_utils.utils import transcribe_audio


class AudioConverter(DocumentConverter):
    """
    Converts audio files to markdown via extraction of metadata (if `exiftool` is installed), and speech transcription (if `speech_recognition` is installed).
    """

    def __init__(self, config: Config):
        self.config = config

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        ** kwargs: Any,  # Options to pass to the converter
    ) -> Tuple[DocumentConverterResult, StreamInfo]:
        md_content = ""

        # Transcribe
        if 'audio' not in self.config.modalities:
            transcript = transcribe_audio(
                file_stream, magic_type=stream_info.magic_type)
            if transcript:
                md_content += "\n\n### Audio Transcript:\n" + transcript
            return DocumentConverterResult(markdown=md_content.strip(), config=self.config)
        else:
            return DocumentConverterResult(audio_stream=file_stream, stream_info=stream_info, config=self.config)

        # Return the result
