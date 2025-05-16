#!/usr/bin/env python3
"""
Metadata manager interface for the knowledge archival system.
Defines the contract for metadata operations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class IMetadataManager(ABC):
    """Interface for metadata operations (multi-source array)."""
    
    @abstractmethod
    def load_metadata(self) -> List[Dict[str, Any]]:
        """
        Load metadata from storage.
        
        Returns:
            List of metadata objects (one per source)
        """
        pass
        
    @abstractmethod
    def save_metadata(self, metadata: List[Dict[str, Any]]) -> bool:
        """
        Save metadata to storage.
        
        Args:
            metadata: List of metadata objects
            
        Returns:
            True if save was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def update_download_metadata(self, filename: str, file_size: int) -> bool:
        """
        Update metadata with new download information.
        
        Args:
            filename: Name of the downloaded file
            file_size: Size of the downloaded file in bytes
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest version from metadata.
        
        Returns:
            Latest version string or None if no downloads exist
        """
        pass