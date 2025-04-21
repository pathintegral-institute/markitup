# MarkItUp

> [!IMPORTANT]
> MarkItUp is a Python package and command-line utility for converting various files to Markdown (e.g., for indexing, text analysis, etc). 
>
> For more information, and full documentation, see the project [README.md](https://github.com/microsoft/markitup) on GitHub.

## Installation

From PyPI:

```bash
pip install markitup[all]
```

From source:

```bash
git clone git@github.com:microsoft/markitup.git
cd markitup
pip install -e packages/markitup[all]
```

## Usage

### Command-Line

```bash
markitup path-to-file.pdf > document.md
```

### Python API

```python
from markitup import MarkItUp

md = MarkItUp()
result = md.convert("test.xlsx")
print(result.text_content)
```

### More Information

For more information, and full documentation, see the project [README.md](https://github.com/microsoft/markitup) on GitHub.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
