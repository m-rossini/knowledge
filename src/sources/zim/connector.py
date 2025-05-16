#!/usr/bin/env python3
"""
ZIM connector for the knowledge archival system.
Orchestrates the ZIM file download, backup, and verification process.
"""
import logging
from typing import Optional

from src.sources.interfaces.source_connector import ISourceConnector
from src.sources.interfaces.metadata_manager import IMetadataManager
from src.sources.interfaces.download_manager import IDownloadManager
from src.sources.interfaces.backup_manager import IBackupManager
from src.sources.interfaces.verification_service import IVerificationService

class ZimConnector(ISourceConnector):
    """
    Connector for managing ZIM format data from any source.
    Orchestrates the metadata, download, backup, and verification components.
    """
    
    def __init__(self, config, metrics_manager, 
                 metadata_manager: IMetadataManager,
                 download_manager: IDownloadManager,
                 backup_manager: IBackupManager,
                 verification_service: IVerificationService,
                 source_name: str = "zim"):
        """
        Initialize the ZimConnector.
        
        Args:
            config: Configuration manager instance
            metrics_manager: Metrics manager instance
            metadata_manager: Metadata manager component
            download_manager: Download manager component
            backup_manager: Backup manager component
            verification_service: Verification service component
            source_name: Name of the source (for metrics and logging)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics_manager = metrics_manager
        self.source_name = source_name
        
        # Component dependencies through interfaces
        self.metadata_manager = metadata_manager
        self.download_manager = download_manager
        self.backup_manager = backup_manager
        self.verification_service = verification_service
        
        # Initialize metrics references
        self.check_count_metric = self.metrics_manager.get_metric(f"{source_name}_check_count")
        self.download_count_metric = self.metrics_manager.get_metric(f"{source_name}_download_count")
        self.download_failures_metric = self.metrics_manager.get_metric(f"{source_name}_download_failures")
        
        # Current download URL (set during check_for_update)
        self.download_url = None
    
    def check_for_update(self, force: bool = False) -> bool:
        """
        Check if a new ZIM file update is available.
        
        Args:
            force: If True, ignore version comparison and force update
            
        Returns:
            True if an update is available, False otherwise
        """
        self.logger.info(">> ZimConnector::check_for_update Checking for %s updates", self.source_name)
        
        # Increment check count metric
        if self.check_count_metric:
            self.check_count_metric.inc()
        
        try:
            # Find the latest remote file
            latest_file, download_url = self.download_manager.get_latest_remote_file()
            
            if not latest_file or not download_url:
                self.logger.error(">>>> ZimConnector::check_for_update No matching files found on server")
                return False
                
            self.logger.info(">> ZimConnector::check_for_update Latest available file: %s", latest_file)
            
            # Store the download URL for later use
            self.download_url = download_url
            
            # If force download is enabled, skip version checks
            if force:
                self.logger.info(">> ZimConnector::check_for_update Force download enabled, update needed")
                return True
            
            # Check if we have any local file
            latest_local_file = self.download_manager.get_latest_local_file()
            
            if not latest_local_file:
                self.logger.info(">> ZimConnector::check_for_update No local file found, update needed")
                return True
            
            # Check if the remote version is newer than what we have
            if self.download_manager.is_newer_version(latest_file):
                self.logger.info(">> ZimConnector::check_for_update Newer version available, update needed")
                return True
                
            self.logger.info(">> ZimConnector::check_for_update No update needed, already have latest version")
            return False
            
        except Exception as e:
            self.logger.error(">>>> ZimConnector::check_for_update Error checking for update: %s", str(e))
            # In case of error, we return False to avoid unnecessary downloads
            return False
    
    def update_if_needed(self, force: bool = False) -> bool:
        """
        Check for ZIM file updates and download if available.
        Handles the entire update process including backup and verification.
        
        Args:
            force: If True, force download regardless of version comparison
            
        Returns:
            True if the process completed successfully, False otherwise
        """
        try:
            # Check if an update is available
            if not self.check_for_update(force=force):
                self.logger.info(">> ZimConnector::update_if_needed No update needed")
                return True
            
            # Backup current version before downloading
            if not self.backup_manager.backup_current_version():
                self.logger.error(">>>> ZimConnector::update_if_needed Backup failed, aborting update")
                return False
            
            # Download the new version
            if not self.download_manager.download_file(self.download_url):
                self.logger.error(">>>> ZimConnector::update_if_needed Download failed")
                if self.download_failures_metric:
                    self.download_failures_metric.inc()
                return False
            
            # Get the downloaded file path
            target_filename = self.download_url.split('/')[-1]
            file_path = self.download_manager.get_file_path(target_filename)
            
            # Verify the downloaded file
            if not self.verification_service.verify_download(file_path):
                self.logger.error(">>>> ZimConnector::update_if_needed Verification failed")
                return False
            
            self.logger.info(">> ZimConnector::update_if_needed Update completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(">>>> ZimConnector::update_if_needed Update process failed: %s", str(e))
            return False