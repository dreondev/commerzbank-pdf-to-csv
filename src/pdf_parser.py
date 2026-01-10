"""
PDF Parser Module
Extracts raw text from Commerzbank PDF bank statements.
"""

from pathlib import Path
from typing import Optional
import pdfplumber


class PDFParser:
    """
    Handles PDF text extraction using pdfplumber.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize PDF parser.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
    
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            FileNotFoundError: If PDF file does not exist
            ValueError: If PDF cannot be opened or read
        """
        self._validate_pdf_exists(pdf_path)
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = self._extract_pages(pdf)
                return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}") from e
    
    def _validate_pdf_exists(self, pdf_path: Path) -> None:
        """
        Validate that PDF file exists.
        
        Args:
            pdf_path: Path to validate
            
        Raises:
            FileNotFoundError: If file does not exist
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def _extract_pages(self, pdf: pdfplumber.PDF) -> str:
        """
        Extract text from all pages in PDF.
        
        Args:
            pdf: Opened pdfplumber PDF object
            
        Returns:
            Combined text from all pages
        """
        pages_text = []
        
        for page in pdf.pages:
            page_text = self._extract_page_text(page)
            if page_text:
                pages_text.append(page_text)
        
        return "\n".join(pages_text)
    
    def _extract_page_text(self, page: pdfplumber.page.Page) -> Optional[str]:
        """
        Extract text from a single page.
        
        Args:
            page: pdfplumber page object
            
        Returns:
            Extracted text or None if page is empty
        """
        text = page.extract_text()
        return text if text else None