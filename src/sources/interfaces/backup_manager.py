#!/usr/bin/env python3
"""
Backup manager interface for the knowledge archival system.
Defines the contract for backup operations.
"""
from abc import ABC, abstractmethod

class IBackupManager(ABC):
    """Interface for backup operations."""
    
    @abstractmethod
    def backup_current_version(self) -> bool:
        """
        Backup the current version.
        
        Returns:
            True if backup was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def cleanup_old_backups(self) -> None:
        """
        Remove old backup files, keeping only recent ones.
        """
        pass