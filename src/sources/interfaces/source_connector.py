#!/usr/bin/env python3
"""
Source connector interface for the knowledge archival system.
Defines the contract for all source connectors.
"""
from abc import ABC, abstractmethod

class ISourceConnector(ABC):
    """Base interface for all knowledge source connectors."""
    
    @abstractmethod
    def update_if_needed(self, force: bool = False) -> bool:
        """
        Check for updates and download if available.
        
        Args:
            force: If True, force download regardless of version comparison
            
        Returns:
            True if the process completed successfully, False otherwise
        """
        pass
        
    @abstractmethod
    def check_for_update(self, force: bool = False) -> bool:
        """
        Check if a new update is available.
        
        Args:
            force: If True, ignore version comparison and force update
            
        Returns:
            True if an update is available, False otherwise
        """
        pass