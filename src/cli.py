"""
Command Line Interface Module
Handles argument parsing and validation.
"""

import argparse


def parse_arguments() -> argparse.Namespace:
    """
    Parse and validate command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Convert Commerzbank PDF bank statements to CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/statement.pdf
  %(prog)s /path/to/statements/
  %(prog)s /path/to/statement.pdf --output /custom/output/
        """
    )
    
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to PDF file or directory containing PDF files"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Custom output directory (default: 'csv' folder in input directory)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser.parse_args()