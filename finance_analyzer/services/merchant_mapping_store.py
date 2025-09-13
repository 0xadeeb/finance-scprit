"""MerchantMappingStore abstracts persistence of merchant->category mappings.

Refactor step: logic moved out of TransactionProcessor without changing
observable behavior.
"""
from __future__ import annotations

import json
import tempfile
import os
from typing import Dict, Optional, Tuple

from ..file_access import FileAccessor


class MerchantMappingStore:
    FILENAME = "merchant_category.json"

    def __init__(self, file_accessor: FileAccessor, temp_file_tracker=None):
        self.file_accessor = file_accessor
        self.temp_file_tracker = temp_file_tracker
        self._file_id: Optional[str] = None  # path or cloud file id
        self._dirty: bool = False

    @property
    def file_id(self) -> Optional[str]:
        return self._file_id

    def load(self, bank_folder_id: str) -> Dict[str, str]:
        """Load existing mapping else return empty dict.
        Handles both local and cloud access patterns.
        Side effect: sets self._file_id when found/created.
        """
        filename = self.FILENAME
        mapping: Dict[str, str] = {}

        if hasattr(self.file_accessor, "find_file_in_folder"):
            file_id = self.file_accessor.find_file_in_folder(bank_folder_id, filename)
            if file_id:
                print(f"📄 Found existing {filename} (File ID: {file_id})")
                content = self.file_accessor.read_text(file_id)
                if content:
                    try:
                        mapping = json.loads(content)
                        print(f"✅ Loaded {len(mapping)} merchant-category mappings")
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parsing {filename}: {e}. Starting with empty dict.")
                else:
                    print(f"⚠️  Failed to download {filename}. Starting with empty dict.")
                self._file_id = file_id
            else:
                print(f"📄 {filename} not found in Bank folder, will create it")
                self._file_id = None
        else:
            file_path = f"{bank_folder_id}/{filename}"
            if self.file_accessor.exists(file_path):
                print(f"📄 Found existing {filename}")
                content = self.file_accessor.read_text(file_path)
                if content:
                    try:
                        mapping = json.loads(content)
                        print(f"✅ Loaded {len(mapping)} merchant-category mappings")
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parsing {filename}: {e}. Starting with empty dict.")
                else:
                    print(f"⚠️  Failed to read {filename}. Starting with empty dict.")
                self._file_id = file_path
            else:
                print(f"📄 {filename} not found in Bank folder, will create it")
                self._file_id = file_path  # pre-assign for local case

        # Loading resets dirty state
        self._dirty = False
        return mapping

    def save(self, bank_folder_id: str, mapping: Dict[str, str]) -> bool:
        if not mapping:
            self._dirty = False
            return True
        if not self._dirty:
            # No changes since load; skip write
            return True
        filename = self.FILENAME
        content = json.dumps(mapping, indent=2)

        # Existing file id/path -> direct write
        if self._file_id:
            success = self.file_accessor.write_text(self._file_id, content)
            if success:
                print(f"✅ Updated {filename} with {len(mapping)} mappings")
                self._dirty = False
            return success

        # Create new file
        if hasattr(self.file_accessor, "find_file_in_folder"):
            # Cloud: need temp file for upload
            try:
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                if self.temp_file_tracker:
                    self.temp_file_tracker(tmp_path)
                success = self.file_accessor.upload_from_temp(tmp_path, f"{bank_folder_id}/{filename}")
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
                if success:
                    new_id = self.file_accessor.find_file_in_folder(bank_folder_id, filename)
                    if new_id:
                        self._file_id = new_id
                        print(f"✅ Created {filename} with {len(mapping)} mappings")
                        self._dirty = False
                        return True
                return False
            except Exception as e:
                print(f"❌ Error creating {filename}: {e}")
                return False
        else:
            file_path = f"{bank_folder_id}/{filename}"
            success = self.file_accessor.write_text(file_path, content)
            if success:
                self._file_id = file_path
                print(f"✅ Created {filename} with {len(mapping)} mappings")
                self._dirty = False
            return success

    # ---------------- Dirty flag management -----------------
    @property
    def dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self) -> None:
        self._dirty = True

    def clear_dirty(self) -> None:
        self._dirty = False
