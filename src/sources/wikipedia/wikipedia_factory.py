#!/usr/bin/env python3
"""
Factory for creating Wikipedia connector and its components.
Handles instantiation and dependency injection for Wikipedia components.
"""
import os
import logging
from typing import Dict, Any

from src.sources.wikipedia.connector import WikipediaConnector
from src.sources.wikipedia.implementations.wikipedia_metadata_manager import WikipediaMetadataManager
from src.sources.wikipedia.implementations.wikipedia_download_manager import WikipediaDownloadManager
from src.sources.wikipedia.implementations.wikipedia_backup_manager import WikipediaBackupManager
from src.sources.wikipedia.implementations.wikipedia_verification_service import WikipediaVerificationService

class WikipediaFactory:
    """Factory for creating Wikipedia connector and its components."""
    
    @staticmethod
    def create_connector(config, metrics_manager):
        """
        Create a fully configured WikipediaConnector with all its components.
        
        Args:
            config: Configuration manager
            metrics_manager: Metrics manager
            
        Returns:
            Configured WikipediaConnector instance
        """
        logger = logging.getLogger(__name__)
        logger.debug("> WikipediaFactory::create_connector Creating Wikipedia connector components")
        
        # Get configuration values
        zim_source_url = config.get("wikipedia.zim_source_url", "https://download.kiwix.org/zim/wikipedia/")
        file_pattern = config.get("wikipedia.file_pattern", "wikipedia_en_all_maxi_[0-9]{4}-[0-9]{2}.zim")
        data_dir = config.get("wikipedia.storage_path", "data/wikipedia")
        backup_dir = config.get("wikipedia.backup_path", "backup/wikipedia")
        max_backups = config.get("wikipedia.max_backups", 3)
        
        # Ensure directories exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create components
        metadata_manager = WikipediaMetadataManager(data_dir)
        
        download_manager = WikipediaDownloadManager(
            zim_source_url, 
            file_pattern, 
            data_dir, 
            metadata_manager, 
            metrics_manager
        )
        
        backup_manager = WikipediaBackupManager(
            data_dir, 
            backup_dir, 
            download_manager, 
            max_backups, 
            metrics_manager
        )
        
        verification_service = WikipediaVerificationService()
        
        # Create and return the connector
        logger.info(">> WikipediaFactory::create_connector Wikipedia connector components created successfully")
        return WikipediaConnector(
            config, 
            metrics_manager, 
            metadata_manager, 
            download_manager, 
            backup_manager, 
            verification_service
        )