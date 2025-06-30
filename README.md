# MarkItUp

This is a fork of [MarkItDown](https://github.com/microsoft/markitdown).

While markitdown is a useful tool, its returned content is too text-focused, which is not updated to the current rise of multi-modal LLMs.

## Features

- Converts various file formats to markdown-oriented OpenAI compatible responses
- Supports multiple file types including:
  - Documents: DOCX (not DOC)
  - Presentations: PPTX (not PPT)
  - Spreadsheets: XLSX, XLS, CSV
  - Media: Audio files (MP3, M4A)
  - Web content: HTML
  - PDF files
  - Plain text files
- Returns OpenAI compatible response, which can be used by most LLM clients
- Supports command line usage

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/pathintegral-institute/markitup.git@main#subdirectory=packages/markitup
```

```bash
uv add git+https://github.com/pathintegral-institute/markitup.git@main#subdirectory=packages/markitup
```

To use audio transciption using `pydub`, install `markitup[audio]`:
```bash
uv add "git+https://github.com/pathintegral-institute/markitup.git@main#subdirectory=packages/markitup[audio]"
```


## Usage
```python
from markitup.converter_utils.utils import read_files_to_bytestreams
from markitup import MarkItUp, Config

fs = read_files_to_bytestreams('packages/markitup/tests/test_files')

miu = MarkItUp(
    config=Config(
        modalities=['image', 'audio'],
        image_use_webp=True
        )
    )

result, stream_info = miu.convert(stream=fs[file_name], file_name=file_name)

```

## Development

### Running Tests

To run the test suite, first install [Hatch](https://hatch.pypa.io/) (which provides better test isolation):

```bash
uv tool install hatch
```

Then navigate to the package directory and run the tests:

```bash
cd packages/markitup
hatch test
```

Or for verbose output:

```bash
cd packages/markitup
hatch test -- -v
```

The test suite includes tests for all supported file formats and converter functionality. Hatch provides better isolation from conflicting globally installed packages than other tools.

```
