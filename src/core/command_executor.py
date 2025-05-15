#!/usr/bin/env python3
"""
Command executor for the knowledge archival system.
Handles execution of specific commands.
"""

import logging
from typing import Dict, Any, Optional, List, Union

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
    
    def update_all_zim_sources(self, force_update: bool = False) -> bool:
        """
        Update all ZIM sources defined in the configuration.
        
        Args:
            force_update: If True, force update regardless of version comparison
            
        Returns:
            True if all updates completed successfully, False if any update failed
        """
        self.logger.info(">> CommandExecutor::update_all_zim_sources Updating all configured ZIM sources")
        
        # Get the list of ZIM sources from configuration
        zim_sources = self.config.get("zim_sources", [])
        
        if not zim_sources:
            self.logger.warning(">>> CommandExecutor::update_all_zim_sources No ZIM sources configured")
            return False
        
        # Track success of all updates
        all_success = True
        
        # Update each configured source
        for source_config in zim_sources:
            source_name = source_config.get("name")
            
            if not source_name:
                self.logger.warning(">>> CommandExecutor::update_all_zim_sources Source missing name, skipping")
                all_success = False
                continue
                
            self.logger.info(">> CommandExecutor::update_all_zim_sources Processing source: %s", source_name)
            
            # Create ZIM connector for this source
            zim_connector = ZimFactory.create_connector_from_config(
                self.config,
                self.metrics_manager,
                source_config
            )
            
            # Update this source
            success = zim_connector.update_if_needed(force=force_update)
            
            if success:
                self.logger.info(">> CommandExecutor::update_all_zim_sources %s update completed successfully", source_name)
            else:
                self.logger.error(">>>> CommandExecutor::update_all_zim_sources %s update failed", source_name)
                all_success = False
        
        return all_success
    
    def update_zim_source(self, source_name: str, force_update: bool = False) -> bool:
        """
        Update a specific ZIM source defined in the configuration.
        
        Args:
            source_name: Name of the ZIM source to update
            force_update: If True, force update regardless of version comparison
            
        Returns:
            True if the update completed successfully, False otherwise
        """
        self.logger.info(">> CommandExecutor::update_zim_source Updating ZIM source: %s", source_name)
        
        # Get the list of ZIM sources from configuration
        zim_sources = self.config.get("zim_sources", [])
        
        if not zim_sources:
            self.logger.error(">>>> CommandExecutor::update_zim_source No ZIM sources configured")
            return False
        
        # Find the requested source
        source_config = None
        for config in zim_sources:
            if config.get("name") == source_name:
                source_config = config
                break
        
        if not source_config:
            self.logger.error(">>>> CommandExecutor::update_zim_source Source not found: %s", source_name)
            return False
            
        # Create ZIM connector for this source
        zim_connector = ZimFactory.create_connector_from_config(
            self.config,
            self.metrics_manager,
            source_config
        )
        
        # Update this source
        success = zim_connector.update_if_needed(force=force_update)
        
        if success:
            self.logger.info(">> CommandExecutor::update_zim_source %s update completed successfully", source_name)
        else:
            self.logger.error(">>>> CommandExecutor::update_zim_source %s update failed", source_name)
            
        return success
    
    def update_knowledge_source(self, source_type: str, force_update: bool = False) -> bool:
        """
        Update a specific knowledge source.
        
        Args:
            source_type: Type of knowledge source to update
                        Format: 'zim' for default or 'zim:source_name'
                        Example: 'zim:wikipedia'
            force_update: If True, force update regardless of version comparison
            
        Returns:
            True if the process completed successfully, False otherwise
        """
        self.logger.info(">> CommandExecutor::update_knowledge_source Updating %s knowledge source", source_type)
        
        # If just 'zim', update all ZIM sources
        if source_type.lower() == 'zim':
            return self.update_all_zim_sources(force_update)
        
        # Handle source specification with name
        if source_type.lower().startswith('zim:'):
            # Format is "zim:source_name"
            # Example: "zim:wikipedia"
            parts = source_type.split(':')
            if len(parts) >= 2:
                source_name = parts[1]
                return self.update_zim_source(source_name, force_update)
            else:
                self.logger.error(">>>> CommandExecutor::update_knowledge_source Invalid ZIM source format. Use zim:source_name")
                return False
        
        self.logger.error(">>>> CommandExecutor::update_knowledge_source Unknown source type: %s", source_type)
        return False