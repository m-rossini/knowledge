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
        default="config/config.json", 
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
        "--source",
        metavar="SOURCE_NAME",
        help="Download a specific source by name as defined in configuration"
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

    # If LOG_LEVEL is set in the environment, override args.log_level
    import os
    env_log_level = os.environ.get("LOG_LEVEL")
    if env_log_level:
        args.log_level = env_log_level.upper()

    # Force logging level globally before anything else
    import logging
    log_level = getattr(logging, args.log_level, logging.INFO)
    logging.basicConfig(level=log_level)

    # Create and run the application manager
    app_manager = ApplicationManager()
    return app_manager.run(args)


if __name__ == "__main__":
    sys.exit(main())
