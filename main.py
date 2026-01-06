#!/usr/bin/env python3
"""
Commerzbank PDF to CSV Converter
Main entry point for the application.
"""

import sys
from src.cli import parse_arguments
from src.app import Application


def main() -> int:
    """
    Main entry point.
    
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    args = parse_arguments()
    app = Application(args)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())