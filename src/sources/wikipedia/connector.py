import os
import logging
import time
import requests
import shutil
from datetime import datetime
from typing import Optional, Tuple, Dict
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
        self.data_dir = self.config.get("wikipedia_data_dir", "data/wikipedia")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")
        self.backup_dir = self.config.get("backup_dir", "backup/wikipedia")
        
        # Kiwix download configuration
        self.download_url = self.config.get(
            "wikipedia_download_url",
            "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi.zim"
        )
        self.kiwix_library_url = self.config.get(
            "kiwix_library_url",
            "https://library.kiwix.org/library/library_zim.xml"
        )
        
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
    
    def check_for_update(self) -> bool:
        """
        Check if a new Wikipedia update is available.
        
        Returns:
            True if an update is available, False otherwise
        """
        self.logger.info(">> WikipediaConnector::check_for_update Checking for Wikipedia updates")
        
        # Increment check count metric
        if self.check_count_metric:
            self.check_count_metric.inc()
        
        try:
            # Get modification date and size from HEAD request
            response = requests.head(self.download_url, timeout=30)
            response.raise_for_status()
            
            # Extract headers
            last_modified = response.headers.get('Last-Modified')
            remote_size = int(response.headers.get('Content-Length', '0'))
            remote_etag = response.headers.get('ETag', '').strip('"')
            
            # Check if we have the file and its metadata
            local_file_path = os.path.join(
                self.data_dir, 
                os.path.basename(self.download_url)
            )
            
            if not os.path.exists(local_file_path):
                self.logger.info(">> WikipediaConnector::check_for_update Local file doesn't exist, update needed")
                return True
            
            # Check file size
            local_size = os.path.getsize(local_file_path)
            if local_size != remote_size:
                self.logger.info(
                    ">> WikipediaConnector::check_for_update Size mismatch: local=%d, remote=%d, update needed", 
                    local_size, remote_size
                )
                return True
            
            # Additional checks could be implemented here
            # For example, comparing checksums or last modified dates
            
            self.logger.info(">> WikipediaConnector::check_for_update No update needed")
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
        local_file_path = os.path.join(
            self.data_dir, 
            os.path.basename(self.download_url)
        )
        
        if not os.path.exists(local_file_path):
            self.logger.info(">> WikipediaConnector::backup_current_version No existing file to backup")
            return True
        
        try:
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_filename = f"wikipedia_backup_{timestamp}.zim"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            self.logger.info(
                ">> WikipediaConnector::backup_current_version Backing up to %s", 
                backup_path
            )
            
            # Copy the file
            shutil.copy2(local_file_path, backup_path)
            
            # Verify backup
            if os.path.exists(backup_path) and os.path.getsize(backup_path) == os.path.getsize(local_file_path):
                self.logger.info(">> WikipediaConnector::backup_current_version Backup successful")
                
                # Update metrics
                backup_count_metric = self.metrics_manager.get_metric("backup_count")
                backup_size_metric = self.metrics_manager.get_metric("backup_last_size_bytes")
                
                if backup_count_metric:
                    backup_count_metric.inc()
                if backup_size_metric:
                    backup_size_metric.set(os.path.getsize(backup_path))
                
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
    
    def download_wikipedia(self) -> bool:
        """
        Download the Wikipedia ZIM file.
        
        Returns:
            True if download was successful, False otherwise
        """
        local_file_path = os.path.join(
            self.data_dir, 
            os.path.basename(self.download_url)
        )
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
        local_file_path = os.path.join(
            self.data_dir, 
            os.path.basename(self.download_url)
        )
        
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
    
    def update_if_needed(self) -> bool:
        """
        Check for Wikipedia updates and download if available.
        Handles the entire update process including backup and verification.
        
        Returns:
            True if the process completed successfully, False otherwise
        """
        try:
            # Check if an update is available
            if not self.check_for_update():
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