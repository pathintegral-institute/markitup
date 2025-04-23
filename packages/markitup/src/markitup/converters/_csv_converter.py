import sys
import csv
import io
from typing import BinaryIO, Any
from charset_normalizer import from_bytes
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._schemas import StreamInfo, Config


class CsvConverter(DocumentConverter):
    """
    Converts CSV files to Markdown tables.
    """
    def __init__(self, config: Config):
        self.config = config

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Read the file content
        content = str(from_bytes(file_stream.read()).best())

        # Parse CSV content
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        if not rows:
            return DocumentConverterResult(markdown="")

        # Create markdown table
        markdown_table = []

        # Add header row
        markdown_table.append("| " + " | ".join(rows[0]) + " |")

        # Add separator row
        markdown_table.append("| " + " | ".join(["---"] * len(rows[0])) + " |")

        # Add data rows
        for row in rows[1:]:
            # Make sure row has the same number of columns as header
            while len(row) < len(rows[0]):
                row.append("")
            # Truncate if row has more columns than header
            row = row[: len(rows[0])]
            markdown_table.append("| " + " | ".join(row) + " |")

        result = "\n".join(markdown_table)

        return DocumentConverterResult(markdown=result, config=self.config)
