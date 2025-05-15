#!/usr/bin/env python3
"""
ZIM file implementation of the metadata manager.
Handles metadata for any ZIM file downloads.
"""
import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.sources.interfaces.metadata_manager import IMetadataManager

class ZimMetadataManager(IMetadataManager):
    """Manages metadata for ZIM file downloads (multi-source, array-based)."""
    
    def __init__(self, data_dir: str, source_name: str = None, metadata_filename: str = "downloads_metadata.json"):
        """
        Initialize the metadata manager.
        
        Args:
            data_dir: Directory where metadata is stored
            source_name: Name of the source
            metadata_filename: Name of the metadata file
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        self.metadata_file = os.path.join(self.data_dir, metadata_filename)
        self.source_name = source_name or os.path.basename(data_dir)

    def load_metadata(self) -> List[Dict[str, Any]]:
        """
        Load download metadata from JSON file (array of source objects).
        
        Returns:
            List of metadata objects (one per source)
        """
        if not os.path.exists(self.metadata_file):
            self.logger.debug("> ZimMetadataManager::load_metadata Metadata file not found, creating empty array")
            return []
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                if not isinstance(metadata, list):
                    self.logger.warning(">>> ZimMetadataManager::load_metadata Metadata not array, converting")
                    metadata = [metadata]
                return metadata
        except Exception as e:
            self.logger.error(">>>> ZimMetadataManager::load_metadata Error loading metadata: %s", str(e))
            return []

    def save_metadata(self, metadata: List[Dict[str, Any]]) -> bool:
        """
        Save download metadata to JSON file (array of source objects).
        
        Args:
            metadata: List of metadata objects
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                self.logger.debug("> ZimMetadataManager::save_metadata Metadata saved successfully")
                return True
        except Exception as e:
            self.logger.error(">>>> ZimMetadataManager::save_metadata Error saving metadata: %s", str(e))
            return False

    def update_download_metadata(self, filename: str, file_size: int) -> bool:
        """
        Update download metadata for this source (in array of sources).
        
        Args:
            filename: Name of the downloaded file
            file_size: Size of the downloaded file in bytes
            
        Returns:
            True if update was successful, False otherwise
        """
        match = re.search(r'_(\d{4}-\d{2})\.', filename)
        if not match:
            self.logger.error(">>>> ZimMetadataManager::update_download_metadata Could not extract version from filename")
            return False
        version = match.group(1)
        current_date = datetime.now().isoformat()
        all_metadata = self.load_metadata()
        # Find or create this source's metadata object
        source_meta = None
        for meta in all_metadata:
            if meta.get("source_name") == self.source_name:
                source_meta = meta
                break
        if not source_meta:
            source_meta = {
                "source_name": self.source_name,
                "downloads": [],
                "latest_version": None,
                "latest_download_date": None
            }
            all_metadata.append(source_meta)
        # Create download record
        download_record = {
            "filename": filename,
            "version": version,
            "size_bytes": file_size,
            "download_date": current_date,
            "download_timestamp": datetime.now().timestamp()
        }
        source_meta["downloads"].append(download_record)
        source_meta["latest_version"] = version
        source_meta["latest_download_date"] = current_date
        return self.save_metadata(all_metadata)

    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest version from metadata.
        
        Returns:
            Latest version string or None if no downloads exist
        """
        all_metadata = self.load_metadata()
        for meta in all_metadata:
            if meta.get("source_name") == self.source_name:
                return meta.get("latest_version")
        return None