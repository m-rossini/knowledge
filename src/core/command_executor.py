#!/usr/bin/env python3
"""
Command executor for the knowledge archival system.
Handles execution of specific commands.
"""

import logging
from typing import Dict, Any, Optional

from src.core.config import ConfigManager
from src.metrics.prometheus_metrics import MetricsManager
from src.sources.zim.zim_factory import ZimFactory

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
            source_type: Type of knowledge source to update
                        Format: 'zim' for default or 'zim:source_name:config_prefix'
                        Example: 'zim:wikipedia:wikipedia'
            force_update: If True, force update regardless of version comparison
            
        Returns:
            True if the process completed successfully, False otherwise
        """
        self.logger.info(">> CommandExecutor::update_knowledge_source Updating %s knowledge source", source_type)
        
        # Default case - use 'zim' as source name and config prefix
        source_name = "zim"
        config_prefix = "zim"
        
        # Handle source specification with custom name and prefix
        if source_type.lower().startswith('zim:'):
            # Format is "zim:source_name:config_prefix"
            # Example: "zim:wikipedia:wikipedia"
            parts = source_type.split(':')
            if len(parts) >= 3:
                source_name = parts[1]
                config_prefix = parts[2]
                self.logger.info(">> CommandExecutor::update_knowledge_source Using source name: %s, config prefix: %s", 
                                source_name, config_prefix)
            else:
                self.logger.error(">>>> CommandExecutor::update_knowledge_source Invalid ZIM source format. Use zim:source_name:config_prefix")
                return False
        
        # Create and use ZIM connector
        zim_connector = ZimFactory.create_connector(
            self.config, 
            self.metrics_manager,
            source_name=source_name,
            config_prefix=config_prefix
        )
        success = zim_connector.update_if_needed(force=force_update)
            
        if success:
            self.logger.info(">> CommandExecutor::update_knowledge_source %s update process completed successfully", source_type)
        else:
            self.logger.error(">>>> CommandExecutor::update_knowledge_source %s update process failed", source_type)
                
        return success