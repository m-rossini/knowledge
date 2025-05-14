#!/usr/bin/env python3
"""
Configuration manager for the knowledge archival system.
Loads settings from JSON files and provides access to configuration.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages configuration for the knowledge archival system.
    Loads from JSON files and provides access to configuration settings.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager with a path to the configuration file.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file and perform environment variable substitution."""
        try:
            if not os.path.exists(self.config_path):
                self.logger.error(">>>> ConfigManager::_load_config Configuration file not found: %s", 
                                 self.config_path)
                self.config = {}
                return
                
            # Read the file content
            with open(self.config_path, 'r') as config_file:
                file_content = config_file.read()
                
                # Substitute environment variables
                file_content = self._substitute_env_vars(file_content)
                
                # Parse JSON content
                self.config = json.loads(file_content)
                    
            self.logger.info(">> ConfigManager::_load_config Configuration loaded from %s", 
                           self.config_path)
                
        except Exception as e:
            self.logger.error(">>>> ConfigManager::_load_config Error loading configuration: %s", str(e))
            self.config = {}
    
    def _substitute_env_vars(self, content: str) -> str:
        """
        Substitute environment variables in the configuration content.
        Supports ${VAR} format.
        
        Args:
            content: Raw configuration file content
            
        Returns:
            Content with environment variables substituted
        """
        # Define pattern for ${VAR} format
        pattern = r'\${([a-zA-Z0-9_]+)}'
        
        # Function to replace matches with environment variable values
        def replace_var(match):
            var_name = match.group(1)
            var_value = os.environ.get(var_name, '')
            if not var_value:
                self.logger.warning(">>> ConfigManager::_substitute_env_vars Environment variable %s not found", var_name)
            return var_value
        
        # Perform substitution
        return re.sub(pattern, replace_var, content)
    
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