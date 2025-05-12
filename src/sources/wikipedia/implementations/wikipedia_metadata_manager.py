#!/usr/bin/env python3
"""
Wikipedia-specific implementation of the metadata manager.
Handles metadata for Wikipedia downloads.
"""
import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional

from src.sources.interfaces.metadata_manager import IMetadataManager

class WikipediaMetadataManager(IMetadataManager):
    """Manages metadata for Wikipedia downloads."""
    
    def __init__(self, data_dir: str):
        """
        Initialize the metadata manager.
        
        Args:
            data_dir: Directory where metadata is stored
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        self.metadata_file = os.path.join(self.data_dir, "downloads_metadata.json")
    
    def load_metadata(self) -> Dict[str, Any]:
        """
        Load download metadata from JSON file.
        
        Returns:
            Dictionary containing download metadata
        """
        if not os.path.exists(self.metadata_file):
            self.logger.debug("> WikipediaMetadataManager::load_metadata Metadata file not found, creating empty metadata")
            return {
                "downloads": [],
                "latest_version": None,
                "latest_download_date": None
            }
            
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                self.logger.debug("> WikipediaMetadataManager::load_metadata Metadata loaded successfully")
                return metadata
        except Exception as e:
            self.logger.error(">>>> WikipediaMetadataManager::load_metadata Error loading metadata: %s", str(e))
            return {
                "downloads": [],
                "latest_version": None,
                "latest_download_date": None
            }
    
    def save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Save download metadata to JSON file.
        
        Args:
            metadata: Dictionary containing download metadata
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                self.logger.debug("> WikipediaMetadataManager::save_metadata Metadata saved successfully")
                return True
        except Exception as e:
            self.logger.error(">>>> WikipediaMetadataManager::save_metadata Error saving metadata: %s", str(e))
            return False
    
    def update_download_metadata(self, filename: str, file_size: int) -> bool:
        """
        Update download metadata after successful download.
        
        Args:
            filename: Name of the downloaded file
            file_size: Size of the downloaded file in bytes
            
        Returns:
            True if update was successful, False otherwise
        """
        # Extract version from filename using regex
        match = re.search(r'_(\d{4}-\d{2})\.', filename)
        if not match:
            self.logger.error(">>>> WikipediaMetadataManager::update_download_metadata Could not extract version from filename")
            return False
            
        version = match.group(1)
        current_date = datetime.now().isoformat()
        
        # Load current metadata
        metadata = self.load_metadata()
        
        # Create download record
        download_record = {
            "filename": filename,
            "version": version,
            "size_bytes": file_size,
            "download_date": current_date,
            "download_timestamp": datetime.now().timestamp()
        }
        
        # Add to downloads list
        metadata["downloads"].append(download_record)
        
        # Update latest version info
        metadata["latest_version"] = version
        metadata["latest_download_date"] = current_date
        
        # Save updated metadata
        return self.save_metadata(metadata)
    
    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest version from metadata.
        
        Returns:
            Latest version string or None if no downloads exist
        """
        metadata = self.load_metadata()
        return metadata.get("latest_version")