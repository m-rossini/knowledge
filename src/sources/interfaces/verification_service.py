#!/usr/bin/env python3
"""
Verification service interface for the knowledge archival system.
Defines the contract for verification operations.
"""
from abc import ABC, abstractmethod

class IVerificationService(ABC):
    """Interface for verification operations."""
    
    @abstractmethod
    def verify_download(self, file_path: str) -> bool:
        """
        Verify the integrity of a downloaded file.
        
        Args:
            file_path: Path to the file to verify
            
        Returns:
            True if verification passed, False otherwise
        """
        pass