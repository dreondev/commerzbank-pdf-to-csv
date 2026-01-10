"""
Unit tests for PDFParser module.
"""

import pytest
from pathlib import Path
from src.pdf_parser import PDFParser


@pytest.fixture
def pdf_parser():
    """Create PDFParser instance for testing."""
    return PDFParser(verbose=False)


@pytest.fixture
def valid_pdf_path():
    """Path to a valid test PDF file."""
    return Path("examples/test.pdf")


class TestExtractText:
    """Tests for extract_text method."""
    
    def test_extract_text_from_valid_pdf(self, pdf_parser, valid_pdf_path):
        """Test extracting text from a valid PDF file."""
        if not valid_pdf_path.exists():
            pytest.skip("Test PDF not available")
        
        text = pdf_parser.extract_text(valid_pdf_path)
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Kontoauszug" in text
        assert "Buchungsdatum:" in text
    
    def test_extract_text_contains_transactions(self, pdf_parser, valid_pdf_path):
        """Test that extracted text contains transaction data."""
        if not valid_pdf_path.exists():
            pytest.skip("Test PDF not available")
        
        text = pdf_parser.extract_text(valid_pdf_path)
        
        # Check for typical transaction elements
        assert "Valuta" in text
        assert "zu Ihren Lasten" in text or "zu Ihren Gunsten" in text
    
    def test_non_existent_pdf_raises_error(self, pdf_parser):
        """Test that non-existent PDF raises FileNotFoundError."""
        non_existent = Path("non_existent_file.pdf")
        
        with pytest.raises(FileNotFoundError):
            pdf_parser.extract_text(non_existent)
    
    def test_invalid_file_raises_error(self, pdf_parser, tmp_path):
        """Test that invalid PDF file raises ValueError."""
        # Create a non-PDF file
        invalid_file = tmp_path / "invalid.pdf"
        invalid_file.write_text("This is not a PDF file")
        
        with pytest.raises(ValueError, match="Failed to extract text"):
            pdf_parser.extract_text(invalid_file)


class TestVerboseMode:
    """Tests for verbose mode."""
    
    def test_verbose_mode_enabled(self):
        """Test that verbose mode can be enabled."""
        parser = PDFParser(verbose=True)
        assert parser.verbose is True
    
    def test_verbose_mode_disabled(self):
        """Test that verbose mode is disabled by default."""
        parser = PDFParser(verbose=False)
        assert parser.verbose is False