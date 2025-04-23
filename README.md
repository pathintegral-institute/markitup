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
pip install git+https://github.com/pathintegral-institute/markitup.git
```

```bash
uv add git+https://github.com/pathintegral-institute/markitup.git
```