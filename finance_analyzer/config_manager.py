"""Unified configuration management for the finance analyzer.

This consolidates the previously duplicated ConfigManager implementations into a
single class that provides:
  * Validation of required keys when present
  * Sensible defaults creation if file missing
  * Backwards support for optional local vs cloud operation

Required keys for cloud mode: bank_folder_id, finance_file_id
Optional keys: storage_type (cloud|local), cloud_provider, local_base_path, merchant_category_file_id
"""

from __future__ import annotations

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Central configuration loader/saver.

    Behavior:
      * If the config file does not exist, create it with defaults.
      * If it exists, merge user values over defaults.
      * Validate mandatory identifiers when storage_type == 'cloud'.
    """

    DEFAULTS: Dict[str, Any] = {
        "storage_type": "cloud",          # 'cloud' or 'local'
        "cloud_provider": "google_drive", # active when storage_type == 'cloud'
        "local_base_path": "./data",      # active when storage_type == 'local'
        "finance_file_id": "",            # file ID (cloud) or relative path (local)
        "bank_folder_id": "",             # folder ID (cloud) or relative path (local)
        "merchant_category_file_id": ""    # optional explicit merchant mapping file ref
    }

    REQUIRED_CLOUD_KEYS = ["bank_folder_id", "finance_file_id"]

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = config_path
        self._config: Dict[str, Any] = self._load_and_validate()

    # ---------------------------- Internal helpers -------------------------
    def _load_and_validate(self) -> Dict[str, Any]:
        data: Dict[str, Any]
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"⚠️  Error reading config file {self.config_path}: {e}. Recreating with defaults.")
                loaded = {}
        else:
            print(f"⚠️  Config file {self.config_path} not found. Creating with defaults.")
            loaded = {}

        # Merge defaults (user values override defaults)
        data = {**self.DEFAULTS, **loaded}

        # Basic validation for cloud mode
        if data.get("storage_type", "cloud") == "cloud":
            missing = [k for k in self.REQUIRED_CLOUD_KEYS if not data.get(k)]
            if missing:
                # Do not hard fail—warn so user can populate later
                print(f"⚠️  Missing required cloud configuration keys: {missing}. You must set them before running.")

        # Persist (ensures any new default keys are written back)
        self._persist(data)
        return data

    def _persist(self, config: Dict[str, Any]) -> None:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            print(f"❌ Error saving config: {e}")

    # ---------------------------- Public API -------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self._persist(self._config)

    def update(self, updates: Dict[str, Any]) -> None:
        self._config.update(updates)
        self._persist(self._config)

    # ---------------------------- Properties --------------------------------
    @property
    def storage_type(self) -> str:
        return self._config.get("storage_type", "cloud")

    @property
    def cloud_provider(self) -> str:
        return self._config.get("cloud_provider", "google_drive")

    @property
    def local_base_path(self) -> str:
        return self._config.get("local_base_path", "./data")

    @property
    def finance_file_id(self) -> str:
        return self._config.get("finance_file_id", "")

    @property
    def bank_folder_id(self) -> str:
        return self._config.get("bank_folder_id", "")

    @property
    def merchant_category_file_id(self) -> str:
        return self._config.get("merchant_category_file_id", "")

    # Dictionary-like conveniences
    def __getitem__(self, key: str) -> Any:  # type: ignore[override]
        return self._config[key]

    def __contains__(self, key: str) -> bool:  # type: ignore[override]
        return key in self._config

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._config)

