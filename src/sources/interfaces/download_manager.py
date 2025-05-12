#!/usr/bin/env python3
"""
Download manager interface for the knowledge archival system.
Defines the contract for downloading operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple

class IDownloadManager(ABC):
    """Interface for downloading operations."""
    
    @abstractmethod
    def get_latest_remote_file(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the latest available file from the remote source.
        
        Returns:
            Tuple of (file_name, full_url) if found, (None, None) otherwise
        """
        pass
        
    @abstractmethod
    def get_latest_local_file(self) -> Optional[str]:
        """
        Get the latest downloaded file.
        
        Returns:
            Path to the latest local file if found, None otherwise
        """
        pass
        
    @abstractmethod
    def download_file(self, url: str) -> bool:
        """
        Download a file from the specified URL.
        
        Args:
            url: URL to download from
            
        Returns:
            True if download was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def is_newer_version(self, remote_file: str) -> bool:
        """
        Check if the remote file is newer than local version.
        
        Args:
            remote_file: Name of the remote file
            
        Returns:
            True if remote file is newer, False otherwise
        """
        pass
        
    @abstractmethod
    def get_file_path(self, filename: str) -> str:
        """
        Get the full path to a file in the data directory.
        
        Args:
            filename: Name of the file
            
        Returns:
            Full path to the file
        """
        pass