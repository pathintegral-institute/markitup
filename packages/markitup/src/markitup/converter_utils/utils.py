import os
from io import BytesIO
import speech_recognition as sr
import io
from typing import BinaryIO


def read_files_to_bytestreams(folder_path="packages/markitup/tests/test_files"):
    """
    Reads all files from the specified folder into BytesIO objects.

    Args:
        folder_path (str): Path to the folder containing files

    Returns:
        dict: Dictionary with filenames as keys and BytesIO objects as values
    """
    byte_streams = {}

    # Check if folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' not found")

    # Iterate through all files in the folder
    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file (not a subdirectory)
        if os.path.isfile(file_path):
            # Read file in binary mode
            with open(file_path, "rb") as f:
                # Create BytesIO object with file content
                file_bytes = BytesIO(f.read())
                # Add to dictionary with filename as key
                byte_streams[filename] = file_bytes
                # Reset BytesIO position to beginning
                file_bytes.seek(0)

    return byte_streams


def transcribe_audio(file_stream: BinaryIO, *, magic_type: str = "audio/mpeg") -> str:
    audio_format = 'mp3' if magic_type == 'audio/mpeg' else 'wav' if magic_type == 'audio/x-wav' else None

    match audio_format:
        case 'mp3':
            import pydub
            audio_segment = pydub.AudioSegment.from_file(
                file_stream, format=audio_format)
            audio_source = io.BytesIO()
            audio_segment.export(audio_source, format="wav")
            audio_source.seek(0)
        case 'wav':
            audio_source = file_stream
        case _:
            raise ValueError(f"Unsupported audio format: {magic_type}")

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_source) as source:
        audio = recognizer.record(source)
        transcript = recognizer.recognize_google(audio).strip()
        return "[No speech detected]" if transcript == "" else transcript
