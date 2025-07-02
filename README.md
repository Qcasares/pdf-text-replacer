# PDF Text Replacer

A Python script that replaces text in PDF files based on CSV mappings while preserving the original PDF structure and formatting.

## Features

- **Bulk text replacement** - Replace multiple text strings in one or more PDF files
- **CSV-driven** - Simple CSV file format with 'from' and 'to' columns for managing replacements
- **Format preservation** - Maintains original PDF structure, fonts, and layout
- **Batch processing** - Process single files or entire directories of PDFs
- **Comprehensive logging** - Detailed logs with configurable verbosity levels
- **Error handling** - Robust error handling with informative error messages
- **Progress feedback** - Real-time progress updates and summary statistics

## Requirements

- Python 3.7 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Process a single PDF file:
```bash
python pdf_text_replacer.py replacements.csv input.pdf
```

### Command Line Options

```
positional arguments:
  csv_file              Path to CSV file with replacement mappings
  pdf_files             PDF file(s) to process

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (for single file)
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory (for multiple files)
  -l {DEBUG,INFO,WARNING,ERROR}, --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level (default: INFO)
```

### Examples

**Single file with custom output:**
```bash
python pdf_text_replacer.py replacements.csv document.pdf -o document_updated.pdf
```

**Multiple files with output directory:**
```bash
python pdf_text_replacer.py replacements.csv *.pdf -d processed_pdfs/
```

**Process with debug logging:**
```bash
python pdf_text_replacer.py replacements.csv file.pdf -l DEBUG
```

**Process multiple specific files:**
```bash
python pdf_text_replacer.py replacements.csv file1.pdf file2.pdf file3.pdf
```

## CSV File Format

The CSV file must contain two columns: `from` and `to`

### Example CSV:

```csv
from,to
old company name,New Company Inc.
2023,2024
Lorem ipsum,Sample text
placeholder@email.com,contact@company.com
OLD ADDRESS,123 New Street, City, State 12345
Product A,Product X
Version 1.0,Version 2.0
confidential,public
DRAFT,FINAL
"old, text","new, text"
```

### CSV Guidelines:

- First row must contain headers: `from,to`
- Use quotes for values containing commas
- Empty 'from' values are skipped with a warning
- Duplicate 'from' values generate warnings
- UTF-8 encoding is supported for international characters

## Output

### Processed Files

- By default, processed files are saved as `original_name_replaced.pdf`
- Custom output paths can be specified with `-o` option
- When using `-d`, all processed files are saved to the specified directory

### Logging

- Log files are created in a `logs/` directory
- Log filename format: `pdf_replacer_YYYYMMDD_HHMMSS.log`
- Includes timestamps, log levels, and detailed messages
- Both file and console output are provided

### Console Output

The script provides real-time feedback including:
- Loading status for CSV mappings
- Processing progress for each file
- Number of replacements made per file
- Summary statistics upon completion

## Error Handling

The script includes comprehensive error handling for:

- Missing or invalid CSV files
- Incorrect CSV format (missing required columns)
- Missing or corrupted PDF files
- File permission issues
- Invalid replacement mappings
- PDF processing errors

All errors are logged with detailed messages and stack traces (in DEBUG mode).

## Limitations

- The script works best with text-based PDFs (not scanned images)
- Complex PDF structures with forms or annotations may have limitations
- Very large PDFs may require significant processing time
- Font matching is approximate when replacing text

## Troubleshooting

### Common Issues

**"CSV file not found" error:**
- Ensure the CSV file path is correct
- Use absolute paths if relative paths aren't working

**"No replacements made" message:**
- Check that your search text exactly matches text in the PDF
- Text in PDFs may have hidden formatting or spaces
- Enable DEBUG logging to see detailed search information

**"Permission denied" errors:**
- Ensure you have read permissions for input files
- Ensure you have write permissions for output directory
- Close any PDFs that might be open in other applications

**Memory issues with large PDFs:**
- Process files one at a time instead of in batches
- Consider splitting very large PDFs before processing

## Example Workflow

1. Create your replacements CSV file:
```csv
from,to
ACME Corp,Example Company
info@acme.com,contact@example.com
© 2023,© 2024
```

2. Test on a single file:
```bash
python pdf_text_replacer.py replacements.csv sample.pdf -l DEBUG
```

3. Check the output file and logs

4. Process all files:
```bash
python pdf_text_replacer.py replacements.csv *.pdf -d processed/
```

## License

This script is provided as-is for text replacement in PDF files. Users are responsible for ensuring they have the right to modify the PDF files they process.

## Contributing

Feel free to submit issues, suggestions, or improvements. When reporting issues, please include:
- Python version
- Operating system
- Error messages and log files
- Sample files (if possible)# pdf-text-replacer
