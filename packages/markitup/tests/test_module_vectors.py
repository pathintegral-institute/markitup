#!/usr/bin/env python3 -m pytest
import os
import time
import pytest
import codecs
import base64

from pathlib import Path

if __name__ == "__main__":
    from _test_vectors import GENERAL_TEST_VECTORS, DATA_URI_TEST_VECTORS
else:
    from ._test_vectors import GENERAL_TEST_VECTORS, DATA_URI_TEST_VECTORS

from markitup import (
    MarkItUp,
    UnsupportedFormatException,
    FileConversionException,
    StreamInfo,
)

skip_remote = (
    True if os.environ.get("GITHUB_ACTIONS") else False
)  # Don't run these tests in CI

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")
TEST_FILES_URL = "https://raw.githubusercontent.com/microsoft/markitup/refs/heads/main/packages/markitup/tests/test_files"


@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_guess_stream_info(test_vector):
    """Test the ability to guess stream info."""
    markitup = MarkItUp()

    local_path = os.path.join(TEST_FILES_DIR, test_vector.filename)
    expected_extension = os.path.splitext(test_vector.filename)[1]

    with open(local_path, "rb") as stream:
        guesses = markitup._get_stream_info_guesses(
            stream,
            base_guess=StreamInfo(
                filename=os.path.basename(test_vector.filename),
                local_path=local_path,
                extension=expected_extension,
            ),
        )

        # For some limited exceptions, we can't guarantee the exact
        # mimetype or extension, so we'll special-case them here.
        if test_vector.filename in [
            "test_outlook_msg.msg",
        ]:
            return

        assert guesses[0].mimetype == test_vector.mimetype
        assert guesses[0].extension == expected_extension
        assert guesses[0].charset == test_vector.charset


@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_convert_local(test_vector):
    """Test the conversion of a local file."""
    markitup = MarkItUp()

    result = markitup.convert(
        os.path.join(TEST_FILES_DIR, test_vector.filename), url=test_vector.url
    )
    for string in test_vector.must_include:
        assert string in result.markdown
    for string in test_vector.must_not_include:
        assert string not in result.markdown


@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_convert_stream_with_hints(test_vector):
    """Test the conversion of a stream with full stream info."""
    markitup = MarkItUp()

    stream_info = StreamInfo(
        extension=os.path.splitext(test_vector.filename)[1],
        mimetype=test_vector.mimetype,
        charset=test_vector.charset,
    )

    with open(os.path.join(TEST_FILES_DIR, test_vector.filename), "rb") as stream:
        result = markitup.convert(
            stream, stream_info=stream_info, url=test_vector.url
        )
        for string in test_vector.must_include:
            assert string in result.markdown
        for string in test_vector.must_not_include:
            assert string not in result.markdown


@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_convert_stream_without_hints(test_vector):
    """Test the conversion of a stream with no stream info."""
    markitup = MarkItUp()

    with open(os.path.join(TEST_FILES_DIR, test_vector.filename), "rb") as stream:
        result = markitup.convert(stream, url=test_vector.url)
        for string in test_vector.must_include:
            assert string in result.markdown
        for string in test_vector.must_not_include:
            assert string not in result.markdown


@pytest.mark.skipif(
    skip_remote,
    reason="do not run tests that query external urls",
)
@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_convert_http_uri(test_vector):
    """Test the conversion of an HTTP:// or HTTPS:// URI."""
    markitup = MarkItUp()

    time.sleep(1)  # Ensure we don't hit rate limits

    result = markitup.convert(
        TEST_FILES_URL + "/" + test_vector.filename,
        url=test_vector.url,  # Mock where this file would be found
    )
    for string in test_vector.must_include:
        assert string in result.markdown
    for string in test_vector.must_not_include:
        assert string not in result.markdown


@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_convert_file_uri(test_vector):
    """Test the conversion of a file:// URI."""
    markitup = MarkItUp()

    result = markitup.convert(
        Path(os.path.join(TEST_FILES_DIR, test_vector.filename)).as_uri(),
        url=test_vector.url,
    )
    for string in test_vector.must_include:
        assert string in result.markdown
    for string in test_vector.must_not_include:
        assert string not in result.markdown


@pytest.mark.parametrize("test_vector", GENERAL_TEST_VECTORS)
def test_convert_data_uri(test_vector):
    """Test the conversion of a data URI."""
    markitup = MarkItUp()

    data = ""
    with open(os.path.join(TEST_FILES_DIR, test_vector.filename), "rb") as stream:
        data = base64.b64encode(stream.read()).decode("utf-8")
    mimetype = test_vector.mimetype
    data_uri = f"data:{mimetype};base64,{data}"

    result = markitup.convert(
        data_uri,
        url=test_vector.url,
    )
    for string in test_vector.must_include:
        assert string in result.markdown
    for string in test_vector.must_not_include:
        assert string not in result.markdown


@pytest.mark.parametrize("test_vector", DATA_URI_TEST_VECTORS)
def test_convert_keep_data_uris(test_vector):
    """Test API functionality when keep_data_uris is enabled"""
    markitup = MarkItUp()

    # Test local file conversion
    result = markitup.convert(
        os.path.join(TEST_FILES_DIR, test_vector.filename),
        keep_data_uris=True,
        url=test_vector.url,
    )

    for string in test_vector.must_include:
        assert string in result.markdown
    for string in test_vector.must_not_include:
        assert string not in result.markdown


@pytest.mark.parametrize("test_vector", DATA_URI_TEST_VECTORS)
def test_convert_stream_keep_data_uris(test_vector):
    """Test the conversion of a stream with no stream info."""
    markitup = MarkItUp()

    stream_info = StreamInfo(
        extension=os.path.splitext(test_vector.filename)[1],
        mimetype=test_vector.mimetype,
        charset=test_vector.charset,
    )

    with open(os.path.join(TEST_FILES_DIR, test_vector.filename), "rb") as stream:
        result = markitup.convert(
            stream, stream_info=stream_info, keep_data_uris=True, url=test_vector.url
        )

        for string in test_vector.must_include:
            assert string in result.markdown
        for string in test_vector.must_not_include:
            assert string not in result.markdown


if __name__ == "__main__":
    import sys

    """Runs this file's tests from the command line."""

    # General tests
    for test_function in [
        test_guess_stream_info,
        test_convert_local,
        test_convert_stream_with_hints,
        test_convert_stream_without_hints,
        test_convert_http_uri,
        test_convert_file_uri,
        test_convert_data_uri,
    ]:
        for test_vector in GENERAL_TEST_VECTORS:
            print(
                f"Running {test_function.__name__} on {test_vector.filename}...", end=""
            )
            test_function(test_vector)
            print("OK")

    # Data URI tests
    for test_function in [
        test_convert_keep_data_uris,
        test_convert_stream_keep_data_uris,
    ]:
        for test_vector in DATA_URI_TEST_VECTORS:
            print(
                f"Running {test_function.__name__} on {test_vector.filename}...", end=""
            )
            test_function(test_vector)
            print("OK")

    print("All tests passed!")
