#!/usr/bin/env python3
"""
Configuration manager for the knowledge archival system.
Loads settings from YAML files and provides access to configuration.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages configuration for the knowledge archival system.
    Loads from YAML files and provides access to configuration settings.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager with a path to the configuration file.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as config_file:
                    self.config = yaml.safe_load(config_file)
                self.logger.info(">> ConfigManager::_load_config Configuration loaded from %s", 
                                self.config_path)
            else:
                self.logger.error(">>>> ConfigManager::_load_config Configuration file not found: %s", 
                                 self.config_path)
                self.config = {}
        except Exception as e:
            self.logger.error(">>>> ConfigManager::_load_config Error loading configuration: %s", str(e))
            self.config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The configuration key to look up
            default: The default value to return if key is not found
            
        Returns:
            The configuration value or default if not found
        """
        if "." in key:
            # Handle nested keys with dot notation
            parts = key.split(".")
            current = self.config
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    self.logger.debug("> ConfigManager::get Config key not found: %s, returning default", key)
                    return default
            self.logger.debug("> ConfigManager::get Retrieved config %s: %s", key, current)
            return current
        else:
            # Simple key lookup
            value = self.config.get(key, default)
            self.logger.debug("> ConfigManager::get Retrieved config %s: %s", key, value)
            return value
    
    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """
        Access nested configuration with a list of keys.
        
        Args:
            *keys: A sequence of keys to traverse the nested configuration
            default: The default value to return if the path is not found
            
        Returns:
            The nested configuration value or default if not found
        """
        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                self.logger.debug("> ConfigManager::get_nested Config path not found: %s", keys)
                return default
        return current