#!/usr/bin/env python3
"""
Logging setup for the knowledge archival system.
Configures logging with proper formatting and file rotation.
"""

import os
import logging
import logging.handlers
from typing import Optional

def setup_logging(log_dir: str, log_level: int = logging.INFO, 
                  log_filename: str = "knowledge_archive.log",
                  max_bytes: int = 10485760, backup_count: int = 5) -> None:
    """
    Configure logging for the application following project standards.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO)
        log_filename: Name of the log file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of rotated log files to keep
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create full log path
    log_path = os.path.join(log_dir, log_filename)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter following project standards with prefixes
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    logging.info(">> LoggingSetup::setup_logging Logging configured, writing to %s", log_path)

def get_logger(name):
    """
    Get a logger with the given name, properly formatted according to standards
    
    Args:
        name: Name for the logger (typically class name)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
