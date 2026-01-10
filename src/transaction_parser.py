"""
Transaction Parser Module
Parses transaction data from extracted PDF text.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from src.models import Transaction


class TransactionParser:
    """
    Parses Commerzbank transaction data from PDF text.
    """
    
    # Regex patterns
    STATEMENT_DATE_PATTERN = r'Kontoauszug vom (\d{2}\.\d{2}\.\d{4})'
    BOOKING_DATE_PATTERN = r'Buchungsdatum: (\d{2}\.\d{2}\.\d{4})'
    TRANSACTION_PATTERN = r'^(.+?)\s+(\d{2}\.\d{2})\s+([\d.,]+[-]?)$'
    
    def __init__(self, verbose: bool = False):
        """
        Initialize transaction parser.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.year: Optional[int] = None
    
    def parse(self, text: str) -> List[Transaction]:
        """
        Parse all transactions from PDF text.
        
        Args:
            text: Extracted PDF text
            
        Returns:
            List of Transaction objects
            
        Raises:
            ValueError: If text cannot be parsed
        """
        self._extract_year(text)
        
        lines = text.split('\n')
        transactions = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for booking date marker
            booking_match = re.search(self.BOOKING_DATE_PATTERN, line)
            if booking_match:
                booking_date_str = booking_match.group(1)
                booking_date = self._parse_date(booking_date_str)
                
                # Parse transactions under this booking date
                i += 1
                while i < len(lines):
                    trans = self._try_parse_transaction(lines, i, booking_date)
                    if trans:
                        transactions.append(trans)
                        i += 1
                    else:
                        # Check if next line is a new booking date
                        if re.search(self.BOOKING_DATE_PATTERN, lines[i]):
                            break
                        i += 1
            else:
                i += 1
        
        return transactions
    
    def _extract_year(self, text: str) -> None:
        """
        Extract year from statement header.
        
        Args:
            text: PDF text
            
        Raises:
            ValueError: If year cannot be extracted
        """
        match = re.search(self.STATEMENT_DATE_PATTERN, text)
        if not match:
            raise ValueError("Could not find statement date in PDF")
        
        date_str = match.group(1)
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        self.year = date_obj.year
    
    def _try_parse_transaction(
        self, 
        lines: List[str], 
        index: int, 
        booking_date: datetime
    ) -> Optional[Transaction]:
        """
        Try to parse a transaction from the current line.
        
        Args:
            lines: All lines from PDF
            index: Current line index
            booking_date: Booking date for this transaction
            
        Returns:
            Transaction object or None if line is not a transaction
        """
        line = lines[index].strip()
        
        # Skip empty lines and known non-transaction lines
        if not line or self._is_non_transaction_line(line):
            return None
        
        # Try to match transaction pattern
        match = re.search(self.TRANSACTION_PATTERN, line)
        if not match:
            return None
        
        beschreibung = match.group(1).strip()
        valuta_str = match.group(2)  # DD.MM format
        betrag_str = match.group(3)
        
        # Parse valuta (add year from statement)
        valuta = self._parse_valuta(valuta_str)
        
        # Parse amount
        betrag = self._parse_betrag(betrag_str)
        
        # Collect multi-line description
        full_description = self._collect_description(lines, index + 1, beschreibung)
        
        return Transaction(
            buchungsdatum=booking_date.date(),
            valuta=valuta.date(),
            beschreibung=beschreibung,
            betrag=betrag,
            waehrung="EUR",
            verwendungszweck=full_description
        )
    
    def _is_non_transaction_line(self, line: str) -> bool:
        """
        Check if line is a known non-transaction line.
        
        Args:
            line: Line to check
            
        Returns:
            True if line should be skipped
        """
        skip_patterns = [
            r'^Buchungsdatum:',
            r'End-to-End-Ref',  # Ohne ^ damit es überall matcht
            r'^Mandatsref:',
            r'^Gläubiger-ID:',
            r'^SEPA-',
            r'^Folgeseite',
            r'^Kontoauszug vom',
            r'^Auszug-Nr\.',
            r'^IBAN:',
            r'^BIC',
            r'^Kontowährung',
            r'^Angaben zu den Umsätzen',
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _collect_description(
        self, 
        lines: List[str], 
        start_index: int, 
        initial_desc: str
    ) -> str:
        """
        Collect multi-line transaction description.
        
        Args:
            lines: All lines from PDF
            start_index: Index to start collecting from
            initial_desc: Initial description from transaction line
            
        Returns:
            Full description string
        """
        description_parts = [initial_desc]
        
        # Collect up to 5 lines or until next transaction
        for i in range(start_index, min(start_index + 5, len(lines))):
            line = lines[i].strip()
            
            # Stop if we hit another transaction or booking date
            if re.search(self.TRANSACTION_PATTERN, line):
                break
            if re.search(self.BOOKING_DATE_PATTERN, line):
                break
            if not line:
                continue
            
            # Stop at known markers
            if self._is_non_transaction_line(line):
                continue
            
            description_parts.append(line)
        
        return ' '.join(description_parts)
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string in DD.MM.YYYY format.
        
        Args:
            date_str: Date string
            
        Returns:
            datetime object
        """
        return datetime.strptime(date_str, '%d.%m.%Y')
    
    def _parse_valuta(self, valuta_str: str) -> datetime:
        """
        Parse valuta date (DD.MM format) and add year.
        
        Args:
            valuta_str: Valuta string in DD.MM format
            
        Returns:
            datetime object with year added
        """
        if not self.year:
            raise ValueError("Year not extracted from statement header")
        
        # Add year to valuta
        full_date_str = f"{valuta_str}.{self.year}"
        return datetime.strptime(full_date_str, '%d.%m.%Y')
    
    def _parse_betrag(self, betrag_str: str) -> Decimal:
        """
        Parse amount string in German format.
        
        Args:
            betrag_str: Amount string (e.g., '1.234,56' or '1.234,56-')
            
        Returns:
            Decimal object (negative for debits)
        """
        # Check if amount is negative (ends with -)
        is_negative = betrag_str.endswith('-')
        
        # Remove minus sign
        betrag_str = betrag_str.rstrip('-')
        
        # Convert German format to standard: 1.234,56 -> 1234.56
        betrag_str = betrag_str.replace('.', '').replace(',', '.')
        
        # Convert to Decimal
        amount = Decimal(betrag_str)
        
        # Apply negative sign
        if is_negative:
            amount = -amount
        
        return amount