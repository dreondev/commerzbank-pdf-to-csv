"""
File Handler Module
Handles file and directory operations for PDF and CSV files.
"""

from pathlib import Path
from typing import List


class FileHandler:
    """
    Handles file system operations for the PDF to CSV converter.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize FileHandler.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
    
    def find_pdf_files(self, input_path: Path) -> List[Path]:
        """
        Find all PDF files in the given path.
        
        Args:
            input_path: Path to file or directory
            
        Returns:
            List of Path objects pointing to PDF files
            
        Raises:
            FileNotFoundError: If input_path does not exist
        """
        self._validate_path_exists(input_path)
        
        if input_path.is_file():
            return self._handle_single_file(input_path)
        elif input_path.is_dir():
            return self._handle_directory(input_path)
        else:
            raise ValueError(f"Input path is neither a file nor a directory: {input_path}")
    
    def _validate_path_exists(self, path: Path) -> None:
        """
        Validate that a path exists.
        
        Args:
            path: Path to validate
            
        Raises:
            FileNotFoundError: If path does not exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
    
    def _handle_single_file(self, file_path: Path) -> List[Path]:
        """
        Handle a single file input.
        
        Args:
            file_path: Path to a single file
            
        Returns:
            List containing the file path if it's a PDF
            
        Raises:
            ValueError: If file is not a PDF
        """
        if not self._is_pdf_file(file_path):
            raise ValueError(f"Input file is not a PDF: {file_path}")
        return [file_path]
    
    def _handle_directory(self, dir_path: Path) -> List[Path]:
        """
        Handle a directory input.
        
        Args:
            dir_path: Path to a directory
            
        Returns:
            Sorted list of PDF files in the directory
        """
        pdf_files = [f for f in dir_path.glob("*.pdf") if self._is_pdf_file(f)]
        return sorted(pdf_files)
    
    def _is_pdf_file(self, file_path: Path) -> bool:
        """
        Check if a file is a PDF.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file has .pdf extension, False otherwise
        """
        return file_path.suffix.lower() == '.pdf'
    
    def get_default_output_dir(self, input_path: Path) -> Path:
        """
        Get the default output directory for CSV files.
        
        Args:
            input_path: Original input path (file or directory)
            
        Returns:
            Path object for output directory (parent_dir/csv/)
        """
        base_dir = self._get_base_directory(input_path)
        return base_dir / "csv"
    
    def _get_base_directory(self, path: Path) -> Path:
        """
        Get the base directory for a given path.
        
        Args:
            path: File or directory path
            
        Returns:
            Parent directory if path is a file, otherwise the path itself
        """
        return path.parent if path.is_file() else path
    
    def create_output_directory(self, output_dir: Path) -> None:
        """
        Create output directory if it doesn't exist.
        
        Args:
            output_dir: Path to output directory
            
        Raises:
            PermissionError: If directory cannot be created
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot create output directory: {output_dir}") from e
    
    def get_output_csv_path(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Generate output CSV path from PDF path.
        
        Args:
            pdf_path: Path to source PDF file
            output_dir: Output directory for CSV files
            
        Returns:
            Path object for output CSV file
        """
        csv_filename = self._generate_csv_filename(pdf_path)
        return output_dir / csv_filename
    
    def _generate_csv_filename(self, pdf_path: Path) -> str:
        """
        Generate CSV filename from PDF filename.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            CSV filename with .csv extension
        """
        return pdf_path.stem + ".csv"