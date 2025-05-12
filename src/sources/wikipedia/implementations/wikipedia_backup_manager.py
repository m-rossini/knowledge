#!/usr/bin/env python3
"""
Wikipedia-specific implementation of the backup manager.
Handles backing up Wikipedia ZIM files.
"""
import os
import logging
import shutil
from datetime import datetime

from src.sources.interfaces.backup_manager import IBackupManager
from src.sources.interfaces.download_manager import IDownloadManager

class WikipediaBackupManager(IBackupManager):
    """Manages backups of Wikipedia ZIM files."""
    
    def __init__(self, data_dir: str, backup_dir: str, 
                 download_manager: IDownloadManager, 
                 max_backups: int, metrics_manager):
        """
        Initialize the backup manager.
        
        Args:
            data_dir: Directory where downloads are stored
            backup_dir: Directory where backups are stored
            download_manager: Download manager instance
            max_backups: Maximum number of backups to keep
            metrics_manager: Metrics manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.download_manager = download_manager
        self.max_backups = max_backups
        self.metrics_manager = metrics_manager
    
    def backup_current_version(self) -> bool:
        """
        Backup the current Wikipedia version before downloading a new one.
        
        Returns:
            True if backup was successful, False otherwise
        """
        latest_local_file = self.download_manager.get_latest_local_file()
        
        if not latest_local_file or not os.path.exists(latest_local_file):
            self.logger.info(">> WikipediaBackupManager::backup_current_version No existing file to backup")
            return True
        
        try:
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            original_filename = os.path.basename(latest_local_file)
            backup_filename = f"{os.path.splitext(original_filename)[0]}_backup_{timestamp}.zim"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            self.logger.info(
                ">> WikipediaBackupManager::backup_current_version Backing up to %s", 
                backup_path
            )
            
            # Copy the file
            shutil.copy2(latest_local_file, backup_path)
            
            # Verify backup
            if os.path.exists(backup_path) and os.path.getsize(backup_path) == os.path.getsize(latest_local_file):
                self.logger.info(">> WikipediaBackupManager::backup_current_version Backup successful")
                
                # Update metrics
                backup_count_metric = self.metrics_manager.get_metric("backup_count")
                backup_size_metric = self.metrics_manager.get_metric("backup_last_size_bytes")
                
                if backup_count_metric:
                    backup_count_metric.inc()
                if backup_size_metric:
                    backup_size_metric.set(os.path.getsize(backup_path))
                
                # Clean up old backups
                self.cleanup_old_backups()
                
                return True
            else:
                self.logger.error(">>>> WikipediaBackupManager::backup_current_version Backup verification failed")
                return False
                
        except Exception as e:
            self.logger.error(">>>> WikipediaBackupManager::backup_current_version Backup failed: %s", str(e))
            
            # Update failure metric
            backup_failures_metric = self.metrics_manager.get_metric("backup_failures")
            if backup_failures_metric:
                backup_failures_metric.inc()
                
            return False
    
    def cleanup_old_backups(self) -> None:
        """Remove old backup files, keeping only the most recent ones."""
        try:
            # List all backup files
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zim') and 'backup' in filename:
                    full_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((full_path, os.path.getmtime(full_path)))
                    
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            if len(backup_files) > self.max_backups:
                for file_path, _ in backup_files[self.max_backups:]:
                    self.logger.info(">> WikipediaBackupManager::cleanup_old_backups Removing old backup: %s", file_path)
                    os.remove(file_path)
                    
        except Exception as e:
            self.logger.error(">>>> WikipediaBackupManager::cleanup_old_backups Error cleaning up old backups: %s", str(e))