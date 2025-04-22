import os
from io import BytesIO
from markitup._schemas import StreamInfo
import magic


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


def detect_file_types(file_dict):
    """
    Detects file types for a dictionary of {filename: BytesIO} pairs
    using only magic type (content-based detection)

    Args:
        file_dict (dict): Dictionary with filenames as keys and BytesIO objects as values

    Returns:
        dict: Dictionary with filenames as keys and file type information as values
    """
    result = {}

    for filename, byte_stream in file_dict.items():
        # Get the original position to reset later
        original_position = byte_stream.tell()

        # Reset stream position to beginning
        byte_stream.seek(0)

        # Get file content for analysis
        file_content = byte_stream.read()

        # Use python-magic to determine file type based on content
        magic_type = magic.from_buffer(file_content, mime=True)

        # Determine file category based on magic_type
        if magic_type.startswith("image/"):
            category = "image"
        elif magic_type.startswith("audio/"):
            category = "audio"
        elif magic_type.startswith("video/"):
            category = "video"
        elif (
            magic_type.startswith("application/vnd.ms-excel")
            or magic_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            category = "xls"
        elif (
            magic_type.startswith("application/vnd.ms-powerpoint")
            or magic_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ):
            category = "ppt"
        elif (
            magic_type.startswith("application/msword")
            or magic_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            category = "doc"
        elif magic_type == "application/pdf":
            category = "pdf"
        elif magic_type.startswith("text/"):
            category = "text"
        else:
            category = "other"

        # Store the results
        result[filename] = StreamInfo(magic_type=magic_type, category=category)

        # Reset stream position
        byte_stream.seek(original_position)

    return result
