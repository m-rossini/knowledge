#!/usr/bin/env python3
"""
Main application entry point for the knowledge archival system.
Handles initialization and orchestration of components.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

from src.core.config import ConfigManager
from src.core.logging_setup import setup_logging
from src.metrics.prometheus_metrics import MetricsManager
from src.sources.wikipedia.connector import WikipediaConnector


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
        "--update-wikipedia",
        action="store_true",
        help="Check for Wikipedia updates and download if available"
    )
    return parser.parse_args()


def main():
    """Main application entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    setup_logging(args.log_dir, log_levels[args.log_level])
    logger = logging.getLogger(__name__)
    
    logger.info(">> Main::main Starting Knowledge Archival System")
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(">>>> Main::main Configuration file not found: %s", config_path)
            return 1
        
        config = ConfigManager(str(config_path))
        
        # Initialize metrics
        metrics_port = config.get("metrics.port", 9090)
        metrics_manager = MetricsManager(metrics_port)
        
        # Process command line actions
        if args.update_wikipedia:
            logger.info(">> Main::main Checking for Wikipedia updates")
            wikipedia_connector = WikipediaConnector(config, metrics_manager)
            success = wikipedia_connector.update_if_needed()
            
            if success:
                logger.info(">> Main::main Wikipedia update process completed successfully")
                return 0
            else:
                logger.error(">>>> Main::main Wikipedia update process failed")
                return 1
        
        # If no specific action was requested, just print help
        logger.info(">> Main::main No specific action requested. Use --help for available commands.")
        return 0
        
    except Exception as e:
        logger.error(">>>> Main::main Unhandled exception: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
