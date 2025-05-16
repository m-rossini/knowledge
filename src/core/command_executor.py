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
        self.logger.info(">> CommandExecutor::__init__ Initialized with config: %s", config)
    
    def download_sources(self, force_update: bool = False) -> bool:
        """
        Download all ZIM sources defined in the configuration.
        
        Args:
            force_update: If True, force download regardless of version comparison
            
        Returns:
            True if all downloads completed successfully, False if any download failed
        """
        self.logger.info(">> CommandExecutor::download_sources Downloading all configured ZIM sources")
        
        # Get the list of ZIM sources from configuration
        zim_sources = self.config.get("zim_sources", [])
        self.logger.info(">> CommandExecutor::download_sources Loaded zim_sources from config: %s", zim_sources)
        
        if not zim_sources:
            self.logger.warning(">>> CommandExecutor::download_sources No ZIM sources configured")
            return False
        
        # Track success of all downloads
        all_success = True
        
        # Download each configured source
        for source_config in zim_sources:
            source_name = source_config.get("name")
            self.logger.info(">> CommandExecutor::download_sources Will process source: %s", source_name)
            
            if not source_name:
                self.logger.warning(">>> CommandExecutor::download_sources Source missing name, skipping")
                all_success = False
                continue
                
            self.logger.info(">> CommandExecutor::download_sources Processing source: %s", source_name)
            
            # Create ZIM connector for this source
            zim_connector = ZimFactory.create_connector_from_config(
                self.config,
                self.metrics_manager,
                source_config
            )
            
            # Download this source
            success = zim_connector.update_if_needed(force=force_update)
            
            if success:
                self.logger.info(">> CommandExecutor::download_sources %s download completed successfully", source_name)
            else:
                self.logger.error(">>>> CommandExecutor::download_sources %s download failed", source_name)
                all_success = False
        
        return all_success
    
    def download_source(self, source_name: str, force_update: bool = False) -> bool:
        """
        Download a specific ZIM source defined in the configuration.
        
        Args:
            source_name: Name of the ZIM source to download
            force_update: If True, force download regardless of version comparison
            
        Returns:
            True if the download completed successfully, False otherwise
        """
        self.logger.info(">> CommandExecutor::download_source Downloading ZIM source: %s", source_name)
        
        # Get the list of ZIM sources from configuration
        zim_sources = self.config.get("zim_sources", [])
        self.logger.info(">> CommandExecutor::download_source Loaded zim_sources from config: %s", zim_sources)
        
        if not zim_sources:
            self.logger.error(">>>> CommandExecutor::download_source No ZIM sources configured")
            return False
        
        # Find the requested source
        source_config = None
        for config in zim_sources:
            self.logger.info(">> CommandExecutor::download_source Checking source: %s", config.get("name"))
            if config.get("name") == source_name:
                source_config = config
                break
        
        if not source_config:
            self.logger.error(">>>> CommandExecutor::download_source Source not found: %s", source_name)
            return False
            
        # Create ZIM connector for this source
        zim_connector = ZimFactory.create_connector_from_config(
            self.config,
            self.metrics_manager,
            source_config
        )
        
        # Download this source
        success = zim_connector.update_if_needed(force=force_update)
        
        if success:
            self.logger.info(">> CommandExecutor::download_source %s download completed successfully", source_name)
        else:
            self.logger.error(">>>> CommandExecutor::download_source %s download failed", source_name)
            
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
            return self.download_sources(force_update)
        
        # Handle source specification with name
        if source_type.lower().startswith('zim:'):
            # Format is "zim:source_name"
            # Example: "zim:wikipedia"
            parts = source_type.split(':')
            if len(parts) >= 2:
                source_name = parts[1]
                return self.download_source(source_name, force_update)
            else:
                self.logger.error(">>>> CommandExecutor::update_knowledge_source Invalid ZIM source format. Use zim:source_name")
                return False
        
        self.logger.error(">>>> CommandExecutor::update_knowledge_source Unknown source type: %s", source_type)
        return False