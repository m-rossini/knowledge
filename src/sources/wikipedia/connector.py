import os
import json
import logging
import time
import requests
import shutil
import re
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Any
import hashlib
from pathlib import Path

class WikipediaConnector:
    """
    Connector for downloading Wikipedia data in ZIM format.
    Handles checking for updates, downloading, and verifying files.
    """
    
    def __init__(self, config, metrics_manager):
        """
        Initialize the WikipediaConnector.
        
        Args:
            config: Configuration manager instance
            metrics_manager: Metrics manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics_manager = metrics_manager
        
        # Get configuration values
        self.zim_source_url = self.config.get("wikipedia.zim_source_url", "https://download.kiwix.org/zim/wikipedia/")
        self.file_pattern = self.config.get("wikipedia.file_pattern", "wikipedia_en_all_maxi_[0-9]{4}-[0-9]{2}.zim")
        self.data_dir = self.config.get("wikipedia.storage_path", "data/wikipedia")
        self.backup_dir = self.config.get("wikipedia.backup_path", "backup/wikipedia")
        self.metadata_file = os.path.join(self.data_dir, "downloads_metadata.json")
        
        # Ensure the source URL ends with a slash
        if not self.zim_source_url.endswith('/'):
            self.zim_source_url += '/'
            
        # Create necessary directories
        self._ensure_directories()
        
        # Initialize metrics references
        self.check_count_metric = self.metrics_manager.get_metric("wikipedia_check_count")
        self.download_count_metric = self.metrics_manager.get_metric("wikipedia_download_count")
        self.download_size_metric = self.metrics_manager.get_metric("wikipedia_last_download_size_bytes")
        self.download_time_metric = self.metrics_manager.get_metric("wikipedia_last_download_time_seconds")
        self.download_failures_metric = self.metrics_manager.get_metric("wikipedia_download_failures")
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        self.logger.debug("> WikipediaConnector::_ensure_directories Directories created")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """
        Load download metadata from JSON file.
        
        Returns:
            Dictionary containing download metadata
        """
        if not os.path.exists(self.metadata_file):
            self.logger.debug("> WikipediaConnector::_load_metadata Metadata file not found, creating empty metadata")
            return {
                "downloads": [],
                "latest_version": None,
                "latest_download_date": None
            }
            
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                self.logger.debug("> WikipediaConnector::_load_metadata Metadata loaded successfully")
                return metadata
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::_load_metadata Error loading metadata: %s", str(e))
            return {
                "downloads": [],
                "latest_version": None,
                "latest_download_date": None
            }
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> bool:
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
                self.logger.debug("> WikipediaConnector::_save_metadata Metadata saved successfully")
                return True
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::_save_metadata Error saving metadata: %s", str(e))
            return False
    
    def _update_download_metadata(self, filename: str, file_size: int) -> bool:
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
            self.logger.error(">>>> WikipediaConnector::_update_download_metadata Could not extract version from filename")
            return False
            
        version = match.group(1)
        current_date = datetime.now().isoformat()
        
        # Load current metadata
        metadata = self._load_metadata()
        
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
        return self._save_metadata(metadata)
    
    def _get_latest_remote_file(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the latest available ZIM file from the remote server based on the file pattern.
        
        Returns:
            Tuple of (file_name, full_url) if found, (None, None) otherwise
        """
        try:
            # Get directory listing from the Kiwix server
            response = requests.get(self.zim_source_url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Extract filenames matching our pattern
            pattern = re.compile(f'href="({self.file_pattern})"')
            matches = pattern.findall(content)
            
            if not matches:
                self.logger.warning(">>> WikipediaConnector::_get_latest_remote_file No files matching pattern: %s", self.file_pattern)
                return None, None
                
            # Sort files by name (which includes the date) to get the latest
            latest_file = sorted(matches)[-1]
            full_url = f"{self.zim_source_url}{latest_file}"
            
            self.logger.info(">> WikipediaConnector::_get_latest_remote_file Found latest file: %s", latest_file)
            return latest_file, full_url
            
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::_get_latest_remote_file Error finding latest file: %s", str(e))
            return None, None
            
    def _get_latest_local_file(self) -> Optional[str]:
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
            self.logger.error(">>>> WikipediaConnector::_get_latest_local_file Error finding local file: %s", str(e))
            return None
    
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
    
    def _is_newer_version(self, remote_file: str) -> bool:
        """
        Check if remote file is newer than our latest downloaded version.
        
        Args:
            remote_file: Name of the remote file
            
        Returns:
            True if remote file is newer, False otherwise
        """
        # Load metadata to check the latest version we have
        metadata = self._load_metadata()
        
        # If we have no previous downloads, then this is newer
        if not metadata["latest_version"]:
            return True
            
        # Extract version dates
        remote_date = self._extract_version_date(remote_file)
        
        if not remote_date:
            self.logger.error(">>>> WikipediaConnector::_is_newer_version Could not extract date from remote file")
            # If we can't determine, assume it's not newer to be safe
            return False
            
        # Convert metadata version to datetime for comparison
        latest_version = metadata["latest_version"]
        match = re.match(r'(\d{4})-(\d{2})', latest_version)
        
        if not match:
            self.logger.error(">>>> WikipediaConnector::_is_newer_version Invalid format in metadata version: %s", latest_version)
            return True  # Assume newer if metadata format is invalid
            
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            local_date = datetime(year, month, 1)
            
            # Compare dates
            return remote_date > local_date
        except (ValueError, IndexError):
            self.logger.error(">>>> WikipediaConnector::_is_newer_version Error comparing version dates")
            return True  # Be conservative and assume it's newer
    
    def check_for_update(self, force: bool = False) -> bool:
        """
        Check if a new Wikipedia update is available.
        
        Args:
            force: If True, ignore version comparison and force update
            
        Returns:
            True if an update is available, False otherwise
        """
        self.logger.info(">> WikipediaConnector::check_for_update Checking for Wikipedia updates")
        
        # Increment check count metric
        if self.check_count_metric:
            self.check_count_metric.inc()
        
        try:
            # Find the latest remote file
            latest_file, download_url = self._get_latest_remote_file()
            
            if not latest_file or not download_url:
                self.logger.error(">>>> WikipediaConnector::check_for_update No matching files found on server")
                return False
                
            self.logger.info(">> WikipediaConnector::check_for_update Latest available file: %s", latest_file)
            
            # Store the download URL for later use
            self.download_url = download_url
            
            # If force download is enabled, skip version checks
            if force:
                self.logger.info(">> WikipediaConnector::check_for_update Force download enabled, update needed")
                return True
            
            # Check if we have any local file
            latest_local_file = self._get_latest_local_file()
            
            if not latest_local_file:
                self.logger.info(">> WikipediaConnector::check_for_update No local file found, update needed")
                return True
            
            # Check if the remote version is newer than what we have
            if self._is_newer_version(latest_file):
                self.logger.info(">> WikipediaConnector::check_for_update Newer version available, update needed")
                return True
                
            self.logger.info(">> WikipediaConnector::check_for_update No update needed, already have latest version")
            return False
            
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::check_for_update Error checking for update: %s", str(e))
            # In case of error, we return False to avoid unnecessary downloads
            return False
    
    def backup_current_version(self) -> bool:
        """
        Backup the current Wikipedia version before downloading a new one.
        
        Returns:
            True if backup was successful, False otherwise
        """
        latest_local_file = self._get_latest_local_file()
        
        if not latest_local_file or not os.path.exists(latest_local_file):
            self.logger.info(">> WikipediaConnector::backup_current_version No existing file to backup")
            return True
        
        try:
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            original_filename = os.path.basename(latest_local_file)
            backup_filename = f"{os.path.splitext(original_filename)[0]}_backup_{timestamp}.zim"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            self.logger.info(
                ">> WikipediaConnector::backup_current_version Backing up to %s", 
                backup_path
            )
            
            # Copy the file
            shutil.copy2(latest_local_file, backup_path)
            
            # Verify backup
            if os.path.exists(backup_path) and os.path.getsize(backup_path) == os.path.getsize(latest_local_file):
                self.logger.info(">> WikipediaConnector::backup_current_version Backup successful")
                
                # Update metrics
                backup_count_metric = self.metrics_manager.get_metric("backup_count")
                backup_size_metric = self.metrics_manager.get_metric("backup_last_size_bytes")
                
                if backup_count_metric:
                    backup_count_metric.inc()
                if backup_size_metric:
                    backup_size_metric.set(os.path.getsize(backup_path))
                
                # Clean up old backups
                self._cleanup_old_backups()
                
                return True
            else:
                self.logger.error(">>>> WikipediaConnector::backup_current_version Backup verification failed")
                return False
                
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::backup_current_version Backup failed: %s", str(e))
            
            # Update failure metric
            backup_failures_metric = self.metrics_manager.get_metric("backup_failures")
            if backup_failures_metric:
                backup_failures_metric.inc()
                
            return False
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backup files, keeping only the most recent ones."""
        try:
            max_backups = self.config.get("wikipedia.max_backups", 3)
            
            # List all backup files
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zim') and 'backup' in filename:
                    full_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((full_path, os.path.getmtime(full_path)))
                    
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            if len(backup_files) > max_backups:
                for file_path, _ in backup_files[max_backups:]:
                    self.logger.info(">> WikipediaConnector::_cleanup_old_backups Removing old backup: %s", file_path)
                    os.remove(file_path)
                    
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::_cleanup_old_backups Error cleaning up old backups: %s", str(e))
    
    def download_wikipedia(self) -> bool:
        """
        Download the Wikipedia ZIM file.
        
        Returns:
            True if download was successful, False otherwise
        """
        if not hasattr(self, 'download_url') or not self.download_url:
            self.logger.error(">>>> WikipediaConnector::download_wikipedia No download URL available")
            return False
            
        target_filename = os.path.basename(self.download_url)
        local_file_path = os.path.join(self.data_dir, target_filename)
        temp_file_path = f"{local_file_path}.downloading"
        
        self.logger.info(">> WikipediaConnector::download_wikipedia Starting download from %s", self.download_url)
        
        # Track download time for metrics
        start_time = time.time()
        
        try:
            # Stream the download to handle large files
            with requests.get(self.download_url, stream=True, timeout=3600) as response:
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
                                percent = (downloaded / file_size) * 100 if file_size else 0
                                self.logger.info(
                                    ">> WikipediaConnector::download_wikipedia Downloaded %.2f%% (%d MB / %d MB)",
                                    percent, downloaded / (1024 * 1024), file_size / (1024 * 1024)
                                )
            
            # Move the temp file to the final location
            if os.path.exists(temp_file_path):
                shutil.move(temp_file_path, local_file_path)
                
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
                self._update_download_metadata(target_filename, file_size)
                
                self.logger.info(
                    ">> WikipediaConnector::download_wikipedia Download completed: %d bytes in %.2f seconds",
                    file_size, download_time
                )
                return True
            else:
                raise Exception("Temporary file not found after download")
                
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::download_wikipedia Download failed: %s", str(e))
            
            # Clean up temp file if it exists
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            # Update failure metric
            if self.download_failures_metric:
                self.download_failures_metric.inc()
                
            return False
    
    def verify_download(self) -> bool:
        """
        Verify the integrity of the downloaded file.
        
        Returns:
            True if verification passed, False otherwise
        """
        if not hasattr(self, 'download_url') or not self.download_url:
            self.logger.error(">>>> WikipediaConnector::verify_download No download URL available")
            return False
            
        target_filename = os.path.basename(self.download_url)
        local_file_path = os.path.join(self.data_dir, target_filename)
        
        if not os.path.exists(local_file_path):
            self.logger.error(">>>> WikipediaConnector::verify_download File does not exist: %s", local_file_path)
            return False
        
        try:
            # Basic file size check
            file_size = os.path.getsize(local_file_path)
            if file_size == 0:
                self.logger.error(">>>> WikipediaConnector::verify_download File is empty")
                return False
            
            # Additional verification could be implemented here
            # For example, checking file headers or running consistency checks
            
            self.logger.info(">> WikipediaConnector::verify_download File verification passed")
            return True
            
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::verify_download Verification failed: %s", str(e))
            return False
    
    def update_if_needed(self, force: bool = False) -> bool:
        """
        Check for Wikipedia updates and download if available.
        Handles the entire update process including backup and verification.
        
        Args:
            force: If True, force download regardless of version comparison
            
        Returns:
            True if the process completed successfully, False otherwise
        """
        try:
            # Check if an update is available
            if not self.check_for_update(force=force):
                self.logger.info(">> WikipediaConnector::update_if_needed No update needed")
                return True
            
            # Backup current version before downloading
            if not self.backup_current_version():
                self.logger.error(">>>> WikipediaConnector::update_if_needed Backup failed, aborting update")
                return False
            
            # Download the new version
            if not self.download_wikipedia():
                self.logger.error(">>>> WikipediaConnector::update_if_needed Download failed")
                return False
            
            # Verify the downloaded file
            if not self.verify_download():
                self.logger.error(">>>> WikipediaConnector::update_if_needed Verification failed")
                return False
            
            self.logger.info(">> WikipediaConnector::update_if_needed Update completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(">>>> WikipediaConnector::update_if_needed Update process failed: %s", str(e))
            return False