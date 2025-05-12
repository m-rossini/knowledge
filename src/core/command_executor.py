#!/usr/bin/env python3
"""
Command executor for the knowledge archival system.
Handles execution of specific commands.
"""

import logging
from typing import Dict, Any, Optional

from src.core.config import ConfigManager
from src.metrics.prometheus_metrics import MetricsManager
from src.sources.wikipedia.wikipedia_factory import WikipediaFactory

class CommandExecutor:
    """
    Executes commands for the knowledge archival system.
    Each command is a separate method to follow SRP.
    """
    
    def __init__(self, config: ConfigManager, metrics_manager: MetricsManager):
        """
        Initialize the command executor with necessary dependencies.
        
        Args:
            config: Configuration manager instance
            metrics_manager: Metrics manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics_manager = metrics_manager
    
    def update_knowledge_source(self, source_type: str, force_update: bool = False) -> bool:
        """
        Update a specific knowledge source.
        
        Args:
            source_type: Type of knowledge source to update (e.g., 'wikipedia', 'gutenberg')
            force_update: If True, force update regardless of version comparison
            
        Returns:
            True if the process completed successfully, False otherwise
        """
        self.logger.info(">> CommandExecutor::update_knowledge_source Updating %s knowledge source", source_type)
        
        if source_type.lower() == 'wikipedia':
            wikipedia_connector = WikipediaFactory.create_connector(self.config, self.metrics_manager)
            success = wikipedia_connector.update_if_needed(force=force_update)
            
            if success:
                self.logger.info(">> CommandExecutor::update_knowledge_source %s update process completed successfully", source_type)
            else:
                self.logger.error(">>>> CommandExecutor::update_knowledge_source %s update process failed", source_type)
                
            return success
        else:
            self.logger.error(">>>> CommandExecutor::update_knowledge_source Unknown knowledge source type: %s", source_type)
            return False