#!/usr/bin/env python3
"""
Application manager for the knowledge archival system.
Handles initialization, configuration and orchestration of components.
"""

import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.core.config import ConfigManager
from src.core.logging_setup import setup_logging
from src.metrics.prometheus_metrics import MetricsManager
from src.core.command_executor import CommandExecutor

class ApplicationManager:
    """
    Manages the knowledge archival system application lifecycle.
    Responsible for initialization, configuration, and command routing.
    """
    
    def __init__(self):
        """Initialize the application manager."""
        self.logger = None
        self.config = None
        self.metrics_manager = None
        self.command_executor = None
    
    def setup_logging(self, log_dir: str, log_level: int) -> None:
        """
        Set up logging for the application.
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level
        """
        setup_logging(log_dir, log_level)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("> ApplicationManager::setup_logging Logging configured")
    
    def load_configuration(self, config_path: str) -> bool:
        """
        Load application configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            path = Path(config_path)
            if not path.exists():
                if self.logger:
                    self.logger.error(">>>> ApplicationManager::load_configuration Configuration file not found: %s", path)
                return False
            
            self.config = ConfigManager(str(path))
            if self.logger:
                self.logger.info(">> ApplicationManager::load_configuration Configuration loaded from %s", path)
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(">>>> ApplicationManager::load_configuration Error loading configuration: %s", str(e))
            return False
    
    def initialize_metrics(self) -> bool:
        """
        Initialize metrics collection.
        
        Returns:
            True if metrics were initialized successfully, False otherwise
        """
        try:
            metrics_port = self.config.get("metrics.port", 9090)
            self.metrics_manager = MetricsManager(metrics_port)
            if self.logger:
                self.logger.info(">> ApplicationManager::initialize_metrics Metrics initialized on port %d", metrics_port)
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(">>>> ApplicationManager::initialize_metrics Error initializing metrics: %s", str(e))
            return False
    
    def initialize_components(self) -> bool:
        """
        Initialize application components.
        
        Returns:
            True if components were initialized successfully, False otherwise
        """
        try:
            # Initialize command executor
            self.command_executor = CommandExecutor(self.config, self.metrics_manager)
            if self.logger:
                self.logger.info(">> ApplicationManager::initialize_components Components initialized successfully")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(">>>> ApplicationManager::initialize_components Error initializing components: %s", str(e))
            return False
    
    def initialize(self, args: argparse.Namespace) -> bool:
        """
        Initialize the application with command-line arguments.
        
        Args:
            args: Command-line arguments
            
        Returns:
            True if initialization was successful, False otherwise
        """
        # Setup logging first
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.setup_logging(args.log_dir, log_levels[args.log_level])
        
        self.logger.info(">> ApplicationManager::initialize Starting Knowledge Archival System")
        
        # Load configuration
        if not self.load_configuration(args.config):
            return False
        
        # Initialize metrics
        if not self.initialize_metrics():
            return False
        
        # Initialize components
        if not self.initialize_components():
            return False
        
        return True
    
    def execute_command(self, args: argparse.Namespace) -> int:
        """
        Execute command based on command-line arguments.
        
        Args:
            args: Command-line arguments
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        if hasattr(args, 'update_zim') and args.update_zim:
            # Download all ZIM sources defined in the configuration
            success = self.command_executor.download_sources(force_update=args.force_download)
            return 0 if success else 1
        
        if hasattr(args, 'update_source') and args.update_source:
            # Download a specific ZIM source by name
            source_name = args.update_source
            success = self.command_executor.download_source(source_name, force_update=args.force_download)
            return 0 if success else 1
        
        # If no specific action was requested, just log a message
        self.logger.info(">> ApplicationManager::execute_command No specific action requested. Use --help for available commands.")
        return 0
    
    def run(self, args: argparse.Namespace) -> int:
        """
        Run the application with the provided arguments.
        
        Args:
            args: Command-line arguments
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Initialize the application
            if not self.initialize(args):
                return 1
            
            # Execute requested command
            return self.execute_command(args)
            
        except Exception as e:
            if self.logger:
                self.logger.error(">>>> ApplicationManager::run Unhandled exception: %s", str(e), exc_info=True)
            return 1