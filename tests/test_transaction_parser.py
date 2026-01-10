"""
Unit tests for TransactionParser module.
"""

import pytest
from datetime import date
from decimal import Decimal
from src.transaction_parser import TransactionParser
from src.models import Transaction


@pytest.fixture
def transaction_parser():
    """Create TransactionParser instance for testing."""
    return TransactionParser(verbose=False)


@pytest.fixture
def sample_pdf_text():
    """Sample PDF text with transactions for testing."""
    return """Kontoauszug vom 30.04.2021
Auszug-Nr. 4 Seite-Nr. 1
IBAN: DE00 0000 0000 0000 0000 00
BIC : COBADEFFXXX

Kontowährung Euro zu Ihren Lasten zu Ihren Gunsten
Alter Kontostand vom 31.03.2021 529,26

Angaben zu den Umsätzen Valuta
Buchungsdatum: 01.04.2021
MUSTERFIRMA GMBH 01.04 17,60-
RATE PER 01.04.2021
End-to-End-Ref.: XXXXXXXXXXXXXXXXXXXXXXXX
Mandatsref: XXXXXXXXXXXXXX
SEPA-BASISLASTSCHRIFT wiederholend

TELEKOM TESTSHOP 01.04 24,95-
Mobilfunk Kundenkonto XXXXXXXXXX
End-to-End-Ref.: Zahlbeleg XXXXXXXXXXXX
SEPA-BASISLASTSCHRIFT wiederholend

Buchungsdatum: 06.04.2021
PAYPAL TESTACCOUNT 06.04 0,99-
ONLINESHOP
End-to-End-Ref.: XXXXXXXXXXXXX

SUPERMARKT 06.04 35,63-
Kartenzahlung

Buchungsdatum: 29.04.2021
ARBEITGEBER AG 29.04 592,00
Gehalt 04.2021
End-to-End-Ref.: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Neuer Kontostand vom 30.04.2021 691,03"""


class TestParseTransactions:
    """Tests for parse method."""
    
    def test_parse_returns_list_of_transactions(self, transaction_parser, sample_pdf_text):
        """Test that parse returns a list of Transaction objects."""
        transactions = transaction_parser.parse(sample_pdf_text)
        
        assert isinstance(transactions, list)
        assert len(transactions) > 0
        assert all(isinstance(t, Transaction) for t in transactions)
    
    def test_parse_extracts_correct_number_of_transactions(self, transaction_parser, sample_pdf_text):
        """Test that correct number of transactions are extracted."""
        transactions = transaction_parser.parse(sample_pdf_text)
        
        # Should find 5 transactions in sample text
        assert len(transactions) == 5
    
    def test_parse_first_transaction_details(self, transaction_parser, sample_pdf_text):
        """Test details of first transaction."""
        transactions = transaction_parser.parse(sample_pdf_text)
        
        first = transactions[0]
        assert first.buchungsdatum == date(2021, 4, 1)
        assert first.valuta == date(2021, 4, 1)
        assert "MUSTERFIRMA GMBH" in first.beschreibung
        assert first.betrag == Decimal('-17.60')
        assert first.waehrung == "EUR"
    
    def test_parse_credit_transaction(self, transaction_parser, sample_pdf_text):
        """Test parsing of credit (positive) transaction."""
        transactions = transaction_parser.parse(sample_pdf_text)
        
        # Last transaction should be a credit (592,00)
        credit = transactions[-1]
        assert credit.betrag == Decimal('592.00')
        assert credit.betrag > 0
        assert "ARBEITGEBER AG" in credit.beschreibung
    
    def test_parse_handles_different_booking_dates(self, transaction_parser, sample_pdf_text):
        """Test that transactions with different booking dates are parsed correctly."""
        transactions = transaction_parser.parse(sample_pdf_text)
        
        # Check booking dates
        booking_dates = [t.buchungsdatum for t in transactions]
        assert date(2021, 4, 1) in booking_dates
        assert date(2021, 4, 6) in booking_dates
        assert date(2021, 4, 29) in booking_dates
    
    def test_parse_invalid_text_raises_error(self, transaction_parser):
        """Test that text without statement date raises error."""
        invalid_text = """Some random text
        without proper header
        Buchungsdatum: 01.04.2021"""
        
        with pytest.raises(ValueError, match="Could not find statement date"):
            transaction_parser.parse(invalid_text)


class TestExtractYear:
    """Tests for _extract_year method."""
    
    def test_extract_year_from_header(self, transaction_parser):
        """Test extracting year from statement header."""
        text = "Kontoauszug vom 30.04.2021\nSome other text"
        
        transaction_parser._extract_year(text)
        
        assert transaction_parser.year == 2021
    
    def test_extract_year_different_date(self, transaction_parser):
        """Test extracting year with different date."""
        text = "Kontoauszug vom 15.12.2023\nSome other text"
        
        transaction_parser._extract_year(text)
        
        assert transaction_parser.year == 2023
    
    def test_extract_year_missing_raises_error(self, transaction_parser):
        """Test that missing statement date raises error."""
        text = "Some text without statement date"
        
        with pytest.raises(ValueError, match="Could not find statement date"):
            transaction_parser._extract_year(text)


class TestParseBetrag:
    """Tests for _parse_betrag method."""
    
    def test_parse_negative_amount(self, transaction_parser):
        """Test parsing negative amount."""
        result = transaction_parser._parse_betrag("17,60-")
        
        assert result == Decimal('-17.60')
    
    def test_parse_positive_amount(self, transaction_parser):
        """Test parsing positive amount."""
        result = transaction_parser._parse_betrag("592,00")
        
        assert result == Decimal('592.00')
    
    def test_parse_amount_with_thousands(self, transaction_parser):
        """Test parsing amount with thousands separator."""
        result = transaction_parser._parse_betrag("1.234,56-")
        
        assert result == Decimal('-1234.56')
    
    def test_parse_large_amount(self, transaction_parser):
        """Test parsing large amount."""
        result = transaction_parser._parse_betrag("12.345,67")
        
        assert result == Decimal('12345.67')


class TestParseValuta:
    """Tests for _parse_valuta method."""
    
    def test_parse_valuta_with_year(self, transaction_parser):
        """Test parsing valuta date."""
        transaction_parser.year = 2021
        
        result = transaction_parser._parse_valuta("01.04")
        
        assert result.year == 2021
        assert result.month == 4
        assert result.day == 1
    
    def test_parse_valuta_without_year_raises_error(self, transaction_parser):
        """Test that parsing valuta without year raises error."""
        with pytest.raises(ValueError, match="Year not extracted"):
            transaction_parser._parse_valuta("01.04")


class TestIsNonTransactionLine:
    """Tests for _is_non_transaction_line method."""
    
    def test_skip_buchungsdatum_line(self, transaction_parser):
        """Test that Buchungsdatum line is skipped."""
        assert transaction_parser._is_non_transaction_line("Buchungsdatum: 01.04.2021")
    
    def test_skip_end_to_end_ref_line(self, transaction_parser):
        """Test that End-to-End-Ref line is skipped."""
        assert transaction_parser._is_non_transaction_line("End-to-End-Ref.: 123456")
    
    def test_skip_sepa_line(self, transaction_parser):
        """Test that SEPA line is skipped."""
        assert transaction_parser._is_non_transaction_line("SEPA-BASISLASTSCHRIFT wiederholend")
    
    def test_transaction_line_not_skipped(self, transaction_parser):
        """Test that actual transaction line is not skipped."""
        assert not transaction_parser._is_non_transaction_line("TARGOBANK AG 01.04 17,60-")


class TestVerboseMode:
    """Tests for verbose mode."""
    
    def test_verbose_mode_enabled(self):
        """Test that verbose mode can be enabled."""
        parser = TransactionParser(verbose=True)
        assert parser.verbose is True
    
    def test_verbose_mode_disabled(self):
        """Test that verbose mode is disabled by default."""
        parser = TransactionParser(verbose=False)
        assert parser.verbose is False