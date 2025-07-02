#!/usr/bin/env python3
"""
PDF Text Replacer
A script to replace text in PDF files based on a CSV mapping file.
Preserves PDF structure and formatting while replacing text content.
"""

import csv
import sys
import os
import logging
import argparse
from datetime import datetime
from pathlib import Path
import traceback
from typing import Dict, List, Tuple
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF


class PDFTextReplacer:
    """Handles PDF text replacement operations"""
    
    def __init__(self, csv_path: str, log_level: str = 'INFO'):
        """
        Initialize the PDF Text Replacer
        
        Args:
            csv_path: Path to CSV file containing replacements
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.csv_path = csv_path
        self.replacements = {}
        self.processed_files = 0
        self.total_replacements = 0
        
        # Setup logging
        self.setup_logging(log_level)
        
    def setup_logging(self, log_level: str):
        """Setup logging configuration"""
        log_filename = f'pdf_replacer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized. Log file: {log_dir / log_filename}")
        
    def load_csv_mappings(self) -> bool:
        """
        Load text replacement mappings from CSV file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.csv_path):
                self.logger.error(f"CSV file not found: {self.csv_path}")
                return False
                
            with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate CSV headers
                if 'from' not in reader.fieldnames or 'to' not in reader.fieldnames:
                    self.logger.error("CSV must have 'from' and 'to' columns")
                    return False
                
                # Load replacements
                for row_num, row in enumerate(reader, start=2):
                    from_text = row.get('from', '').strip()
                    to_text = row.get('to', '').strip()
                    
                    if not from_text:
                        self.logger.warning(f"Empty 'from' value in row {row_num}, skipping")
                        continue
                        
                    if from_text in self.replacements:
                        self.logger.warning(f"Duplicate 'from' value '{from_text}' in row {row_num}")
                        
                    self.replacements[from_text] = to_text
                    
                self.logger.info(f"Loaded {len(self.replacements)} replacement mappings")
                
                if not self.replacements:
                    self.logger.warning("No valid replacements found in CSV")
                    return False
                    
                return True
                
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
            
    def replace_text_in_pdf(self, input_path: str, output_path: str) -> Tuple[bool, int]:
        """
        Replace text in a PDF file using PyMuPDF
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output PDF file
            
        Returns:
            Tuple[bool, int]: (Success status, Number of replacements made)
        """
        try:
            if not os.path.exists(input_path):
                self.logger.error(f"Input PDF not found: {input_path}")
                return False, 0
                
            # Open the PDF
            doc = fitz.open(input_path)
            replacement_count = 0
            
            self.logger.info(f"Processing PDF: {input_path}")
            self.logger.info(f"Number of pages: {len(doc)}")
            
            # Process each page
            for page_num, page in enumerate(doc):
                self.logger.debug(f"Processing page {page_num + 1}")
                
                # Get all text instances on the page
                for from_text, to_text in self.replacements.items():
                    # Search for all instances of the text
                    text_instances = page.search_for(from_text)
                    
                    if text_instances:
                        self.logger.debug(f"Found {len(text_instances)} instances of '{from_text}' on page {page_num + 1}")
                        
                        for inst in text_instances:
                            # Create a redaction annotation to hide the original text
                            page.add_redact_annot(inst, text="")
                            
                            # Apply the redaction
                            page.apply_redactions()
                            
                            # Add the replacement text at the same location
                            # Get the font size from the original text
                            text_dict = page.get_text("dict")
                            font_size = 11  # Default font size
                            
                            # Try to get the original font size
                            for block in text_dict["blocks"]:
                                if "lines" in block:
                                    for line in block["lines"]:
                                        for span in line["spans"]:
                                            if from_text in span["text"]:
                                                font_size = span["size"]
                                                break
                            
                            # Insert the replacement text
                            page.insert_text(
                                inst.bottom_left,
                                to_text,
                                fontsize=font_size,
                                color=(0, 0, 0)
                            )
                            replacement_count += 1
                            
            # Save the modified PDF
            doc.save(output_path)
            doc.close()
            
            self.logger.info(f"Successfully created output PDF: {output_path}")
            self.logger.info(f"Total replacements made: {replacement_count}")
            
            return True, replacement_count
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False, 0
            
    def process_pdf_file(self, input_path: str, output_path: str = None) -> bool:
        """
        Process a single PDF file
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF (optional, defaults to input_replaced.pdf)
            
        Returns:
            bool: True if successful
        """
        if not output_path:
            input_file = Path(input_path)
            output_path = input_file.parent / f"{input_file.stem}_replaced{input_file.suffix}"
            
        print(f"\n{'='*60}")
        print(f"Processing: {input_path}")
        print(f"Output: {output_path}")
        print(f"{'='*60}")
        
        success, count = self.replace_text_in_pdf(input_path, output_path)
        
        if success:
            self.processed_files += 1
            self.total_replacements += count
            print(f"✓ Success! Made {count} replacements")
        else:
            print(f"✗ Failed to process file")
            
        return success
        
    def process_multiple_pdfs(self, pdf_files: List[str], output_dir: str = None) -> None:
        """
        Process multiple PDF files
        
        Args:
            pdf_files: List of PDF file paths
            output_dir: Output directory (optional)
        """
        total_files = len(pdf_files)
        print(f"\nProcessing {total_files} PDF files...")
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"\nFile {idx}/{total_files}")
            
            if output_dir:
                output_file = output_path / f"{Path(pdf_file).stem}_replaced.pdf"
            else:
                output_file = None
                
            self.process_pdf_file(pdf_file, output_file)
            
        # Summary
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed successfully: {self.processed_files}/{total_files}")
        print(f"Total replacements made: {self.total_replacements}")
        print(f"Check log file for details")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Replace text in PDF files based on CSV mappings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s replacements.csv input.pdf
  %(prog)s replacements.csv input.pdf -o output.pdf
  %(prog)s replacements.csv *.pdf -d output_folder
  %(prog)s replacements.csv file1.pdf file2.pdf file3.pdf
  
CSV Format:
  The CSV file should have two columns: 'from' and 'to'
  Example:
    from,to
    old text,new text
    Company A,Company B
        """
    )
    
    parser.add_argument('csv_file', help='Path to CSV file with replacement mappings')
    parser.add_argument('pdf_files', nargs='+', help='PDF file(s) to process')
    parser.add_argument('-o', '--output', help='Output file path (for single file)')
    parser.add_argument('-d', '--output-dir', help='Output directory (for multiple files)')
    parser.add_argument('-l', '--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Create replacer instance
    replacer = PDFTextReplacer(args.csv_file, args.log_level)
    
    # Load CSV mappings
    print(f"Loading replacements from: {args.csv_file}")
    if not replacer.load_csv_mappings():
        print("Failed to load CSV mappings. Exiting.")
        sys.exit(1)
        
    # Show loaded replacements
    print(f"\nLoaded {len(replacer.replacements)} replacement mappings:")
    for from_text, to_text in list(replacer.replacements.items())[:5]:
        print(f"  '{from_text}' → '{to_text}'")
    if len(replacer.replacements) > 5:
        print(f"  ... and {len(replacer.replacements) - 5} more")
        
    # Process PDF files
    if len(args.pdf_files) == 1 and not args.output_dir:
        # Single file
        replacer.process_pdf_file(args.pdf_files[0], args.output)
    else:
        # Multiple files
        if args.output and len(args.pdf_files) > 1:
            print("Warning: -o/--output is ignored when processing multiple files")
        replacer.process_multiple_pdfs(args.pdf_files, args.output_dir)


if __name__ == "__main__":
    main()