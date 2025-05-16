#!/usr/bin/env python3
"""
ZIM file implementation of the download manager.
Handles downloading of ZIM files from any source.
"""
import os
import re
import time
import logging
import requests
from datetime import datetime
from typing import Optional, Tuple

from src.sources.interfaces.download_manager import IDownloadManager
from src.sources.interfaces.metadata_manager import IMetadataManager

class ZimDownloadManager(IDownloadManager):
    """Manages downloading of ZIM files from any source."""
    
    def __init__(self, source_url: str, file_pattern: str, data_dir: str, 
                 metadata_manager: IMetadataManager, metrics_manager, source_name: str = "zim"):
        """
        Initialize the download manager.
        
        Args:
            source_url: URL to the ZIM file source
            file_pattern: Regex pattern to match ZIM files
            data_dir: Directory to store downloaded files
            metadata_manager: Metadata manager instance
            metrics_manager: Metrics manager instance
            source_name: Name of the source (for metrics and logging)
        """
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.source_url = source_url
        self.file_pattern = file_pattern
        self.data_dir = data_dir
        self.source_name = source_name
        
        # Ensure the source URL ends with a slash
        if not self.source_url.endswith('/'):
            self.source_url += '/'
            
        # Dependencies
        self.metadata_manager = metadata_manager
        self.metrics_manager = metrics_manager
        
        # Metrics references
        self.download_count_metric = self.metrics_manager.get_metric(f"{source_name}_download_count")
        self.download_size_metric = self.metrics_manager.get_metric(f"{source_name}_last_download_size_bytes")
        self.download_time_metric = self.metrics_manager.get_metric(f"{source_name}_last_download_time_seconds")
        self.download_failures_metric = self.metrics_manager.get_metric(f"{source_name}_download_failures")
        
    def get_latest_remote_file(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the latest available ZIM file from the remote server based on the file pattern.
        
        Returns:
            Tuple of (file_name, full_url) if found, (None, None) otherwise
        """
        try:
            # Get directory listing from the server
            response = requests.get(self.source_url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Extract filenames matching our pattern
            pattern = re.compile(f'href="({self.file_pattern})"')
            matches = pattern.findall(content)
            
            if not matches:
                self.logger.warning(">>> ZimDownloadManager::get_latest_remote_file No files matching pattern: %s", self.file_pattern)
                return None, None
                
            # Sort files by name (which includes the date) to get the latest
            latest_file = sorted(matches)[-1]
            full_url = f"{self.source_url}{latest_file}"
            
            self.logger.info(">> ZimDownloadManager::get_latest_remote_file Found latest file: %s", latest_file)
            return latest_file, full_url
            
        except Exception as e:
            self.logger.error(">>>> ZimDownloadManager::get_latest_remote_file Error finding latest file: %s", str(e))
            return None, None
            
    def get_latest_local_file(self) -> Optional[str]:
        """
        Find the latest downloaded ZIM file in the local storage directory.
        
        Returns:
            Path to the latest local file if found, None otherwise
        """
        try:
            # Create a regex pattern from the file pattern
            pattern_str = self.file_pattern.replace('[0-9]{4}', '\\d{4}').replace('[0-9]{2}', '\\d{2}')
            pattern = re.compile(pattern_str)
            
            matching_files = []
            for filename in os.listdir(self.data_dir):
                if pattern.match(filename):
                    matching_files.append(filename)
                    
            if not matching_files:
                return None
                
            # Sort by name to get the latest version
            latest_file = sorted(matching_files)[-1]
            return os.path.join(self.data_dir, latest_file)
            
        except Exception as e:
            self.logger.error(">>>> ZimDownloadManager::get_latest_local_file Error finding local file: %s", str(e))
            return None
    
    def is_newer_version(self, remote_file: str) -> bool:
        """
        Check if remote file is newer than our latest downloaded version.
        
        Args:
            remote_file: Name of the remote file
            
        Returns:
            True if remote file is newer, False otherwise
        """
        # Get the latest version from metadata
        latest_version = self.metadata_manager.get_latest_version()
        
        # If we have no previous downloads, then this is newer
        if not latest_version:
            return True
            
        # Extract version dates
        remote_date = self._extract_version_date(remote_file)
        
        if not remote_date:
            self.logger.error(">>>> ZimDownloadManager::is_newer_version Could not extract date from remote file")
            # If we can't determine, assume it's not newer to be safe
            return False
            
        # Convert metadata version to datetime for comparison
        match = re.match(r'(\d{4})-(\d{2})', latest_version)
        
        if not match:
            self.logger.error(">>>> ZimDownloadManager::is_newer_version Invalid format in metadata version: %s", latest_version)
            return True  # Assume newer if metadata format is invalid
            
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            local_date = datetime(year, month, 1)
            
            # Compare dates
            return remote_date > local_date
        except (ValueError, IndexError):
            self.logger.error(">>>> ZimDownloadManager::is_newer_version Error comparing version dates")
            return True  # Be conservative and assume it's newer
            
    def _extract_version_date(self, filename: str) -> Optional[datetime]:
        """
        Extract version date from filename.
        
        Args:
            filename: Filename to extract version from
            
        Returns:
            datetime object if version was successfully extracted, None otherwise
        """
        match = re.search(r'_(\d{4})-(\d{2})\.', filename)
        if not match:
            return None
            
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            return datetime(year, month, 1)
        except (ValueError, IndexError):
            return None
            
    def download_file(self, url: str) -> bool:
        """
        Download a file from the specified URL.
        
        Args:
            url: URL to download from
            
        Returns:
            True if download was successful, False otherwise
        """
        target_filename = os.path.basename(url)
        local_file_path = os.path.join(self.data_dir, target_filename)
        temp_file_path = f"{local_file_path}.downloading"
        
        self.logger.info(">> ZimDownloadManager::download_file Starting download from %s", url)
        self.logger.info(">> ZimDownloadManager::download_file Using temporary file path: %s", temp_file_path)
        self.logger.info(">> ZimDownloadManager::download_file Final destination path: %s", local_file_path)
        
        # Track download time for metrics
        start_time = time.time()
        
        try:
            # Stream the download to handle large files
            with requests.get(url, stream=True, timeout=3600) as response:
                response.raise_for_status()
                file_size = int(response.headers.get('Content-Length', 0))
                
                with open(temp_file_path, 'wb') as f:
                    downloaded = 0
                    chunk_size = 1024 * 1024  # 1 MB chunks
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Log progress every 100MB
                            if downloaded % (100 * chunk_size) == 0:
                                # Calculate elapsed time
                                elapsed_time = time.time() - start_time
                                
                                # Calculate download rate (bytes per second)
                                download_rate = downloaded / elapsed_time if elapsed_time > 0 else 0
                                
                                # Calculate ETA (estimated time of arrival) in seconds
                                remaining_bytes = file_size - downloaded
                                eta_seconds = remaining_bytes / download_rate if download_rate > 0 else 0
                                
                                # Format elapsed time and ETA for display (HH:MM:SS)
                                elapsed_str = self._format_time_hms(elapsed_time)
                                eta_str = self._format_time_hms(eta_seconds)
                                
                                percent = (downloaded / file_size) * 100 if file_size else 0
                                
                                self.logger.info(
                                    ">> ZimDownloadManager::download_file Downloaded %.2f%% (%d MB / %d MB) | Elapsed: %s | ETA: %s | Speed: %.2f MB/s",
                                    percent, 
                                    downloaded / (1024 * 1024), 
                                    file_size / (1024 * 1024),
                                    elapsed_str,
                                    eta_str,
                                    download_rate / (1024 * 1024)
                                )
            
            # Move the temp file to the final location
            if os.path.exists(temp_file_path):
                os.rename(temp_file_path, local_file_path)
                self.logger.info(">> ZimDownloadManager::download_file Renamed temporary file to final path: %s", local_file_path)
                
                # Update metrics
                download_time = time.time() - start_time
                file_size = os.path.getsize(local_file_path)
                
                if self.download_count_metric:
                    self.download_count_metric.inc()
                if self.download_size_metric:
                    self.download_size_metric.set(file_size)
                if self.download_time_metric:
                    self.download_time_metric.set(download_time)
                
                # Update metadata after successful download
                self.metadata_manager.update_download_metadata(target_filename, file_size)
                
                # Format total download time for display
                formatted_time = self._format_time_hms(download_time)
                
                self.logger.info(
                    ">> ZimDownloadManager::download_file Download completed: %d MB in %s (%.2f MB/s)",
                    file_size / (1024 * 1024),
                    formatted_time,
                    (file_size / (1024 * 1024)) / download_time if download_time > 0 else 0
                )
                return True
            else:
                raise Exception("Temporary file not found after download")
                
        except Exception as e:
            self.logger.error(">>>> ZimDownloadManager::download_file Download failed: %s", str(e))
            
            # Clean up temp file if it exists
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                self.logger.info(">> ZimDownloadManager::download_file Cleaned up temporary file: %s", temp_file_path)
            
            # Update failure metric
            if self.download_failures_metric:
                self.download_failures_metric.inc()
                
            return False
            
    def _format_time_hms(self, seconds: float) -> str:
        """
        Format time in seconds to a human-readable HH:MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string (HH:MM:SS)
        """
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
    def get_file_path(self, filename: str) -> str:
        """
        Get the full path to a file in the data directory.
        
        Args:
            filename: Name of the file
            
        Returns:
            Full path to the file
        """
        return os.path.join(self.data_dir, filename)