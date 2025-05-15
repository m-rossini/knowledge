#!/usr/bin/env python3
"""
Factory for creating ZIM connector and its components.
Handles instantiation and dependency injection for generic ZIM components.
"""
import os
import logging
from typing import Dict, Any

from src.sources.zim.connector import ZimConnector
from src.sources.zim.implementations.zim_metadata_manager import ZimMetadataManager
from src.sources.zim.implementations.zim_download_manager import ZimDownloadManager
from src.sources.zim.implementations.zim_backup_manager import ZimBackupManager
from src.sources.zim.implementations.zim_verification_service import ZimVerificationService

class ZimFactory:
    """Factory for creating ZIM connector and its components."""
    
    @staticmethod
    def create_connector(config, metrics_manager, source_name: str = "zim", config_prefix: str = "zim"):
        """
        Create a fully configured ZimConnector with all its components.
        
        Args:
            config: Configuration manager
            metrics_manager: Metrics manager
            source_name: Name of the source (for metrics and logging)
            config_prefix: Prefix for configuration keys
            
        Returns:
            Configured ZimConnector instance
        """
        logger = logging.getLogger(__name__)
        logger.debug("> ZimFactory::create_connector Creating ZIM connector components for %s", source_name)
        
        # Get configuration values
        source_url = config.get(f"{config_prefix}.source_url", "https://download.kiwix.org/zim/")
        file_pattern = config.get(f"{config_prefix}.file_pattern", ".*_[0-9]{4}-[0-9]{2}.zim")
        data_dir = config.get(f"{config_prefix}.storage_path", f"data/{source_name}")
        backup_dir = config.get(f"{config_prefix}.backup_path", f"backup/{source_name}")
        max_backups = config.get(f"{config_prefix}.max_backups", 3)
        
        # Ensure directories exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create components
        metadata_manager = ZimMetadataManager(data_dir)
        
        download_manager = ZimDownloadManager(
            source_url, 
            file_pattern, 
            data_dir, 
            metadata_manager, 
            metrics_manager,
            source_name
        )
        
        backup_manager = ZimBackupManager(
            data_dir, 
            backup_dir, 
            download_manager, 
            max_backups, 
            metrics_manager,
            source_name
        )
        
        verification_service = ZimVerificationService()
        
        # Create and return the connector
        logger.info(">> ZimFactory::create_connector ZIM connector components created successfully for %s", source_name)
        return ZimConnector(
            config, 
            metrics_manager, 
            metadata_manager, 
            download_manager, 
            backup_manager, 
            verification_service,
            source_name
        )