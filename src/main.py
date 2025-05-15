#!/usr/bin/env python3
"""
Main application entry point for the knowledge archival system.
Handles initialization and orchestration of components.
"""

import sys
import argparse

from src.core.application_manager import ApplicationManager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Knowledge Archival System")
    parser.add_argument(
        "--config", 
        default="config/config.yaml", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-dir", 
        default="logs", 
        help="Directory for log files"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    parser.add_argument(
        "--update-zim",
        metavar="SOURCE",
        help="Check for updates of ZIM files. Can be 'zim' for default configuration or "
             "'zim:source_name:config_prefix' for specific sources (e.g., 'zim:wikipedia:wikipedia')"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force download even if the file exists or is not newer"
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Create and run the application manager
    app_manager = ApplicationManager()
    return app_manager.run(args)


if __name__ == "__main__":
    sys.exit(main())
