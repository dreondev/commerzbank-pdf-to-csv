"""
Application Module
Main application logic and orchestration.
"""

import argparse
from pathlib import Path
from typing import List
from src.file_handler import FileHandler
from src.logger import Logger


class Application:
    """
    Main application class that orchestrates the conversion process.
    """
    
    def __init__(self, args: argparse.Namespace):
        """
        Initialize the application.
        
        Args:
            args: Parsed command line arguments
        """
        self.args = args
        self.logger = Logger(verbose=args.verbose)
        self.file_handler = FileHandler(verbose=args.verbose)
        self.input_path = Path(args.input_path)
        self.output_dir = Path(args.output) if args.output else None
    
    def run(self) -> int:
        """
        Run the main application logic.
        
        Returns:
            int: Exit code (0 = success, 1 = error)
        """
        try:
            # Step 1: Find PDF files
            pdf_files = self._find_pdf_files()
            if not pdf_files:
                self.logger.error(f"No PDF files found in: {self.input_path}")
                return 1
            
            # Step 2: Setup output directory
            output_dir = self._setup_output_directory()
            
            # Step 3: Display summary
            self._display_summary(pdf_files, output_dir)
            
            # Step 4: Process PDFs (not yet implemented)
            self._process_pdfs(pdf_files, output_dir)
            
            return 0
            
        except FileNotFoundError as e:
            self.logger.error(str(e))
            return 1
        except PermissionError as e:
            self.logger.error(f"Permission denied: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if self.args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _find_pdf_files(self) -> List[Path]:
        """
        Find all PDF files based on input path.
        
        Returns:
            List of PDF file paths
        """
        return self.file_handler.find_pdf_files(self.input_path)
    
    def _setup_output_directory(self) -> Path:
        """
        Setup and create output directory.
        
        Returns:
            Path to output directory
        """
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = self.file_handler.get_default_output_dir(self.input_path)
        
        self.file_handler.create_output_directory(output_dir)
        return output_dir
    
    def _display_summary(self, pdf_files: List[Path], output_dir: Path) -> None:
        """
        Display processing summary.
        
        Args:
            pdf_files: List of PDF files to process
            output_dir: Output directory path
        """
        self.logger.info(f"Found {len(pdf_files)} PDF file(s)")
        self.logger.info(f"Output directory: {output_dir}")
        
        if self.args.verbose:
            self.logger.info("\nPDF files found:")
            for pdf in pdf_files:
                self.logger.info(f"  {pdf}")
    
    def _process_pdfs(self, pdf_files: List[Path], output_dir: Path) -> None:
        """
        Process all PDF files and convert to CSV.
        
        Args:
            pdf_files: List of PDF files to process
            output_dir: Output directory for CSV files
        """
        # TODO: Implement in Module 2
        self.logger.warning("PDF processing not yet implemented (coming in Module 2)")
        self.logger.success("Module 1 (CLI & File Handler) completed successfully")