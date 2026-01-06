"""
Unit tests for FileHandler module.
"""

import pytest
from pathlib import Path
from src.file_handler import FileHandler


@pytest.fixture
def file_handler():
    """Create FileHandler instance for testing."""
    return FileHandler(verbose=False)


@pytest.fixture
def temp_pdf_structure(tmp_path):
    """
    Create temporary directory structure with PDF files for testing.
    
    Structure:
        tmp_path/
        ├── file1.pdf
        ├── file2.pdf
        └── not_a_pdf.txt
    """
    # Create PDF files in root
    (tmp_path / "file1.pdf").touch()
    (tmp_path / "file2.pdf").touch()
    (tmp_path / "not_a_pdf.txt").touch()
    
    return tmp_path


class TestFindPdfFiles:
    """Tests for find_pdf_files method."""
    
    def test_find_single_pdf_file(self, file_handler, temp_pdf_structure):
        """Test finding a single PDF file."""
        pdf_path = temp_pdf_structure / "file1.pdf"
        result = file_handler.find_pdf_files(pdf_path)
        
        assert len(result) == 1
        assert result[0] == pdf_path
    
    def test_find_pdfs_in_directory(self, file_handler, temp_pdf_structure):
        """Test finding PDFs in a directory."""
        result = file_handler.find_pdf_files(temp_pdf_structure)
        
        assert len(result) == 2
        assert all(pdf.suffix == ".pdf" for pdf in result)
        assert temp_pdf_structure / "file1.pdf" in result
        assert temp_pdf_structure / "file2.pdf" in result
    
    def test_non_existent_path_raises_error(self, file_handler):
        """Test that non-existent path raises FileNotFoundError."""
        non_existent = Path("/non/existent/path")
        
        with pytest.raises(FileNotFoundError):
            file_handler.find_pdf_files(non_existent)
    
    def test_non_pdf_file_raises_error(self, file_handler, temp_pdf_structure):
        """Test that non-PDF file raises ValueError."""
        txt_file = temp_pdf_structure / "not_a_pdf.txt"
        
        with pytest.raises(ValueError, match="not a PDF"):
            file_handler.find_pdf_files(txt_file)
    
    def test_empty_directory_returns_empty_list(self, file_handler, tmp_path):
        """Test that empty directory returns empty list."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = file_handler.find_pdf_files(empty_dir)
        assert result == []


class TestGetDefaultOutputDir:
    """Tests for get_default_output_dir method."""
    
    def test_output_dir_for_file(self, file_handler, temp_pdf_structure):
        """Test output directory for a single file."""
        pdf_file = temp_pdf_structure / "file1.pdf"
        result = file_handler.get_default_output_dir(pdf_file)
        
        assert result == temp_pdf_structure / "csv"
    
    def test_output_dir_for_directory(self, file_handler, temp_pdf_structure):
        """Test output directory for a directory."""
        result = file_handler.get_default_output_dir(temp_pdf_structure)
        
        assert result == temp_pdf_structure / "csv"


class TestCreateOutputDirectory:
    """Tests for create_output_directory method."""
    
    def test_create_new_directory(self, file_handler, tmp_path):
        """Test creating a new output directory."""
        output_dir = tmp_path / "csv"
        
        assert not output_dir.exists()
        file_handler.create_output_directory(output_dir)
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_create_nested_directory(self, file_handler, tmp_path):
        """Test creating nested directories."""
        output_dir = tmp_path / "level1" / "level2" / "csv"
        
        file_handler.create_output_directory(output_dir)
        assert output_dir.exists()
    
    def test_existing_directory_no_error(self, file_handler, tmp_path):
        """Test that existing directory doesn't raise error."""
        output_dir = tmp_path / "csv"
        output_dir.mkdir()
        
        # Should not raise any error
        file_handler.create_output_directory(output_dir)
        assert output_dir.exists()


class TestGetOutputCsvPath:
    """Tests for get_output_csv_path method."""
    
    def test_csv_path_generation(self, file_handler, tmp_path):
        """Test generating CSV path from PDF path."""
        pdf_path = tmp_path / "statement_2023.pdf"
        output_dir = tmp_path / "csv"
        
        result = file_handler.get_output_csv_path(pdf_path, output_dir)
        
        assert result == output_dir / "statement_2023.csv"
        assert result.suffix == ".csv"
    
    def test_csv_path_preserves_filename(self, file_handler, tmp_path):
        """Test that CSV filename matches PDF filename."""
        pdf_path = tmp_path / "Kontoauszug_Januar_2023.pdf"
        output_dir = tmp_path / "csv"
        
        result = file_handler.get_output_csv_path(pdf_path, output_dir)
        
        assert result.stem == "Kontoauszug_Januar_2023"