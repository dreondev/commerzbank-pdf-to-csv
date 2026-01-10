"""Data models for Commerzbank transactions."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Transaction:
    """Represents a single bank transaction from a Commerzbank statement.
    
    Attributes:
        buchungsdatum: Date when the transaction was booked
        valuta: Value date (when the transaction takes effect)
        beschreibung: Transaction description/purpose
        betrag: Transaction amount (negative for debits, positive for credits)
        waehrung: Currency code (e.g., 'EUR')
        gegenkonto_iban: Counter-party IBAN (if available)
        gegenkonto_bic: Counter-party BIC (if available)
        verwendungszweck: Full purpose/reference text
    """
    
    buchungsdatum: date
    valuta: date
    beschreibung: str
    betrag: Decimal
    waehrung: str = "EUR"
    gegenkonto_iban: Optional[str] = None
    gegenkonto_bic: Optional[str] = None
    verwendungszweck: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for CSV export.
        
        Returns:
            Dictionary with all transaction fields
        """
        return {
            'buchungsdatum': self.buchungsdatum.strftime('%d.%m.%Y'),
            'valuta': self.valuta.strftime('%d.%m.%Y'),
            'beschreibung': self.beschreibung,
            'betrag': self._format_betrag(),
            'waehrung': self.waehrung,
            'gegenkonto_iban': self.gegenkonto_iban or '',
            'gegenkonto_bic': self.gegenkonto_bic or '',
            'verwendungszweck': self.verwendungszweck or ''
        }
    
    def _format_betrag(self) -> str:
        """Format amount in German format with comma as decimal separator.
        
        Returns:
            Formatted amount string (e.g., '1.234,56' or '−1.234,56')
        """
        # Convert Decimal to float for formatting
        amount = float(self.betrag)
        
        # Format with German locale (comma as decimal separator)
        if amount < 0:
            # Use minus sign (U+2212) for negative amounts
            formatted = f"−{abs(amount):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return formatted
    
    def is_debit(self) -> bool:
        """Check if transaction is a debit (outgoing payment).
        
        Returns:
            True if amount is negative (debit), False otherwise
        """
        return self.betrag < 0
    
    def is_credit(self) -> bool:
        """Check if transaction is a credit (incoming payment).
        
        Returns:
            True if amount is positive (credit), False otherwise
        """
        return self.betrag > 0