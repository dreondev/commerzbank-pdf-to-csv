"""
CSV Writer Module
Writes transaction data to CSV files in Commerzbank format.
"""

import csv
from pathlib import Path
from typing import List
from src.models import Transaction


class CSVWriter:
    """
    Writes transactions to CSV files in Commerzbank format.
    """
    
    # Commerzbank CSV format specification
    DELIMITER = ';'
    QUOTECHAR = '"'
    ENCODING = 'utf-8'
    
    # CSV header (Commerzbank format)
    HEADER = [
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
    
    def __init__(self, verbose: bool = False):
        """
        Initialize CSV writer.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
    
    def write(
        self, 
        transactions: List[Transaction], 
        output_path: Path
    ) -> None:
        """
        Write transactions to CSV file.
        
        Args:
            transactions: List of Transaction objects
            output_path: Path to output CSV file
            
        Raises:
            ValueError: If transactions list is empty
            PermissionError: If file cannot be written
        """
        if not transactions:
            raise ValueError("Cannot write CSV: transactions list is empty")
        
        self._validate_output_path(output_path)
        
        try:
            with open(output_path, 'w', newline='', encoding=self.ENCODING) as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=self.HEADER,
                    delimiter=self.DELIMITER,
                    quotechar=self.QUOTECHAR,
                    quoting=csv.QUOTE_ALL
                )
                
                # Write header
                writer.writeheader()
                
                # Write transactions
                for transaction in transactions:
                    row = self._transaction_to_row(transaction)
                    writer.writerow(row)
                    
        except PermissionError as e:
            raise PermissionError(f"Cannot write to file: {output_path}") from e
    
    def _validate_output_path(self, output_path: Path) -> None:
        """
        Validate output path.
        
        Args:
            output_path: Path to validate
            
        Raises:
            ValueError: If path is not a .csv file
        """
        if output_path.suffix.lower() != '.csv':
            raise ValueError(f"Output file must have .csv extension: {output_path}")
    
    def _transaction_to_row(self, transaction: Transaction) -> dict:
        """
        Convert Transaction object to CSV row dictionary.
        
        Args:
            transaction: Transaction object
            
        Returns:
            Dictionary with CSV column names as keys
        """
        # Determine transaction type (Umsatzart)
        umsatzart = self._get_umsatzart(transaction)
        
        return {
            'Buchungstag': transaction.buchungsdatum.strftime('%d.%m.%Y'),
            'Wertstellung': transaction.valuta.strftime('%d.%m.%Y'),
            'Umsatzart': umsatzart,
            'Buchungstext': transaction.verwendungszweck or transaction.beschreibung,
            'Betrag': self._format_betrag(transaction.betrag),
            'Währung': transaction.waehrung,
            'Auftraggeberkonto': '',  # Not available in PDF
            'Bankleitzahl Auftraggeberkonto': '',  # Not available in PDF
            'IBAN Auftraggeberkonto': transaction.gegenkonto_iban or ''
        }
    
    def _get_umsatzart(self, transaction: Transaction) -> str:
        """
        Determine transaction type (Umsatzart).
        
        Args:
            transaction: Transaction object
            
        Returns:
            Transaction type string
        """
        if transaction.is_debit():
            return 'Lastschrift'
        else:
            return 'Gutschrift'
    
    def _format_betrag(self, betrag) -> str:
        """
        Format amount in German format with comma as decimal separator.
        
        Args:
            betrag: Decimal amount
            
        Returns:
            Formatted amount string (e.g., '1.234,56' or '−1.234,56')
        """
        # Convert Decimal to float for formatting
        amount = float(betrag)
        
        # Format with German locale (comma as decimal separator)
        if amount < 0:
            # Use minus sign (U+2212) for negative amounts
            formatted = f"−{abs(amount):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return formatted