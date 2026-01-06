"""
Logger Module
Professional logging with different severity levels.
"""

from typing import Optional


class Logger:
    """
    Simple logger with different severity levels.
    """
    
    # ANSI color codes for terminal output
    COLORS = {
        'ERROR': '\033[91m',    # Red
        'WARNING': '\033[93m',  # Yellow
        'SUCCESS': '\033[92m',  # Green
        'INFO': '\033[94m',     # Blue
        'RESET': '\033[0m'      # Reset
    }
    
    def __init__(self, verbose: bool = False):
        """
        Initialize logger.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
    
    def _format_message(self, level: str, message: str) -> str:
        """
        Format message with severity level.
        
        Args:
            level: Severity level (ERROR, WARNING, SUCCESS, INFO)
            message: Message to format
            
        Returns:
            Formatted message string
        """
        color = self.COLORS.get(level, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        return f"{color}[{level}]{reset} {message}"
    
    def error(self, message: str) -> None:
        """Log error message."""
        print(self._format_message('ERROR', message))
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        print(self._format_message('WARNING', message))
    
    def success(self, message: str) -> None:
        """Log success message."""
        print(self._format_message('SUCCESS', message))
    
    def info(self, message: str) -> None:
        """Log info message."""
        print(self._format_message('INFO', message))
    
    def debug(self, message: str) -> None:
        """Log debug message (only in verbose mode)."""
        if self.verbose:
            print(f"[DEBUG] {message}")