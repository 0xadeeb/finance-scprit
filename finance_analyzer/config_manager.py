"""
Configuration management for the finance analyzer.
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "storage_type": "cloud",  # "local" or "cloud"
            "cloud_provider": "google_drive",  # Only used if storage_type is "cloud"
            "local_base_path": "./data",  # Only used if storage_type is "local"
            "finance_file_id": "",  # For cloud: file ID, for local: relative path
            "bank_folder_id": "",  # For cloud: folder ID, for local: relative path
            "merchant_category_file_id": ""  # For cloud: file ID, for local: relative path
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(config)
                    return default_config
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading config: {e}. Using defaults.")
        else:
            print(f"⚠️  Config file {self.config_path} not found. Creating with defaults.")
            self._save_config(default_config)
        
        return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"❌ Error saving config: {e}")
    
    @property
    def storage_type(self) -> str:
        return self.config.get('storage_type', 'cloud')
    
    @property
    def cloud_provider(self) -> str:
        return self.config.get('cloud_provider', 'google_drive')
    
    @property
    def local_base_path(self) -> str:
        return self.config.get('local_base_path', './data')
    
    @property
    def finance_file_id(self) -> str:
        return self.config.get('finance_file_id', '')
    
    @property
    def bank_folder_id(self) -> str:
        return self.config.get('bank_folder_id', '')
    
    @property
    def merchant_category_file_id(self) -> str:
        return self.config.get('merchant_category_file_id', '')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        self._save_config(self.config)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
        self._save_config(self.config)

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"{self.config_file} not found. Please create it with your Google Drive file/folder IDs. "
                "See SETUP_INSTRUCTIONS.md for details."
            )
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Validate required keys
        required_keys = ['bank_folder_id', 'finance_file_id']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        # Set default cloud provider if not specified
        if 'cloud_provider' not in config:
            config['cloud_provider'] = 'google_drive'
        
        return config
    
    @property
    def bank_folder_id(self) -> str:
        """Get the bank folder ID"""
        return self._config['bank_folder_id']
    
    @property
    def finance_file_id(self) -> str:
        """Get the finance file ID"""
        return self._config['finance_file_id']
    
    @property
    def cloud_provider(self) -> str:
        """Get the cloud storage provider"""
        return self._config.get('cloud_provider', 'google_drive')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access"""
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in config"""
        return key in self._config
