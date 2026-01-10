"""
Unit tests for CSVWriter module.
"""

import pytest
import csv
from pathlib import Path
from datetime import date
from decimal import Decimal
from src.csv_writer import CSVWriter
from src.models import Transaction


@pytest.fixture
def csv_writer():
    """Create CSVWriter instance for testing."""
    return CSVWriter(verbose=False)


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing."""
    return [
        Transaction(
            buchungsdatum=date(2021, 4, 1),
            valuta=date(2021, 4, 1),
            beschreibung="MUSTERFIRMA GMBH",
            betrag=Decimal('-17.60'),
            waehrung="EUR",
            verwendungszweck="RATE PER 01.04.2021"
        ),
        Transaction(
            buchungsdatum=date(2021, 4, 1),
            valuta=date(2021, 4, 1),
            beschreibung="TELEKOM TESTSHOP",
            betrag=Decimal('-24.95'),
            waehrung="EUR"
        ),
        Transaction(
            buchungsdatum=date(2021, 4, 29),
            valuta=date(2021, 4, 29),
            beschreibung="ARBEITGEBER AG",
            betrag=Decimal('592.00'),
            waehrung="EUR",
            gegenkonto_iban="DE00000000000000000000"
        )
    ]


class TestWriteCSV:
    """Tests for write method."""
    
    def test_write_creates_csv_file(self, csv_writer, sample_transactions, tmp_path):
        """Test that CSV file is created."""
        output_path = tmp_path / "output.csv"
        
        csv_writer.write(sample_transactions, output_path)
        
        assert output_path.exists()
        assert output_path.is_file()
    
    def test_write_csv_has_correct_header(self, csv_writer, sample_transactions, tmp_path):
        """Test that CSV has correct header row."""
        output_path = tmp_path / "output.csv"
        
        csv_writer.write(sample_transactions, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            header = next(reader)
            
            assert header == [
                'Buchungstag',
                'Wertstellung',
                'Umsatzart',
                'Buchungstext',
                'Betrag',
                'Währung',
                'Auftraggeberkonto',
                'Bankleitzahl Auftraggeberkonto',
                'IBAN Auftraggeberkonto'
            ]
    
    def test_write_csv_has_correct_number_of_rows(self, csv_writer, sample_transactions, tmp_path):
        """Test that CSV has correct number of data rows."""
        output_path = tmp_path / "output.csv"
        
        csv_writer.write(sample_transactions, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Skip header
            rows = list(reader)
            
            assert len(rows) == 3
    
    def test_write_debit_transaction(self, csv_writer, sample_transactions, tmp_path):
        """Test writing debit transaction."""
        output_path = tmp_path / "output.csv"
        
        csv_writer.write(sample_transactions, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Skip header
            first_row = next(reader)
            
            assert first_row[0] == '01.04.2021'  # Buchungstag
            assert first_row[1] == '01.04.2021'  # Wertstellung
            assert first_row[2] == 'Lastschrift'  # Umsatzart
            assert first_row[3] == 'MUSTERFIRMA GMBH'  # Buchungstext
            assert first_row[4] == '−17,60'  # Betrag (German format with minus sign)
            assert first_row[5] == 'EUR'  # Währung
    
    def test_write_credit_transaction(self, csv_writer, sample_transactions, tmp_path):
        """Test writing credit transaction."""
        output_path = tmp_path / "output.csv"
        
        csv_writer.write(sample_transactions, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Skip header
            next(reader)  # Skip first row
            next(reader)  # Skip second row
            third_row = next(reader)
            
            assert third_row[2] == 'Gutschrift'  # Umsatzart
            assert third_row[4] == '592,00'  # Betrag (positive)
            assert third_row[8] == 'DE00000000000000000000'  # IBAN
    
    def test_write_empty_transactions_raises_error(self, csv_writer, tmp_path):
        """Test that empty transactions list raises error."""
        output_path = tmp_path / "output.csv"
        
        with pytest.raises(ValueError, match="transactions list is empty"):
            csv_writer.write([], output_path)
    
    def test_write_invalid_extension_raises_error(self, csv_writer, sample_transactions, tmp_path):
        """Test that invalid file extension raises error."""
        output_path = tmp_path / "output.txt"
        
        with pytest.raises(ValueError, match="must have .csv extension"):
            csv_writer.write(sample_transactions, output_path)
    
    def test_write_permission_error(self, csv_writer, sample_transactions, tmp_path):
        """Test handling of permission errors."""
        output_path = tmp_path / "readonly.csv"
        output_path.touch()
        output_path.chmod(0o444)  # Read-only
        
        try:
            with pytest.raises(PermissionError, match="Cannot write to file"):
                csv_writer.write(sample_transactions, output_path)
        finally:
            output_path.chmod(0o644)  # Restore permissions


class TestFormatBetrag:
    """Tests for _format_betrag method."""
    
    def test_format_negative_amount(self, csv_writer):
        """Test formatting negative amount."""
        result = csv_writer._format_betrag(Decimal('-17.60'))
        
        assert result == '−17,60'
    
    def test_format_positive_amount(self, csv_writer):
        """Test formatting positive amount."""
        result = csv_writer._format_betrag(Decimal('592.00'))
        
        assert result == '592,00'
    
    def test_format_amount_with_thousands(self, csv_writer):
        """Test formatting amount with thousands separator."""
        result = csv_writer._format_betrag(Decimal('-1234.56'))
        
        assert result == '−1.234,56'
    
    def test_format_large_amount(self, csv_writer):
        """Test formatting large amount."""
        result = csv_writer._format_betrag(Decimal('12345.67'))
        
        assert result == '12.345,67'


class TestGetUmsatzart:
    """Tests for _get_umsatzart method."""
    
    def test_debit_transaction_type(self, csv_writer):
        """Test transaction type for debit."""
        transaction = Transaction(
            buchungsdatum=date(2021, 4, 1),
            valuta=date(2021, 4, 1),
            beschreibung="TEST",
            betrag=Decimal('-100.00')
        )
        
        result = csv_writer._get_umsatzart(transaction)
        
        assert result == 'Lastschrift'
    
    def test_credit_transaction_type(self, csv_writer):
        """Test transaction type for credit."""
        transaction = Transaction(
            buchungsdatum=date(2021, 4, 1),
            valuta=date(2021, 4, 1),
            beschreibung="TEST",
            betrag=Decimal('100.00')
        )
        
        result = csv_writer._get_umsatzart(transaction)
        
        assert result == 'Gutschrift'


class TestVerboseMode:
    """Tests for verbose mode."""
    
    def test_verbose_mode_enabled(self):
        """Test that verbose mode can be enabled."""
        writer = CSVWriter(verbose=True)
        assert writer.verbose is True
    
    def test_verbose_mode_disabled(self):
        """Test that verbose mode is disabled by default."""
        writer = CSVWriter(verbose=False)
        assert writer.verbose is False