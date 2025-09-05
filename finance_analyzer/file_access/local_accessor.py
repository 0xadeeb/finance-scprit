"""
Local file system accessor implementation.
"""

import os
import shutil
import glob
from typing import Optional, List
from .base import FileAccessor


class LocalFileAccessor(FileAccessor):
    """File accessor for local file system"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = os.path.abspath(base_path)
    
    def _resolve_path(self, path: str) -> str:
        """Resolve relative path to absolute path"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_path, path)
    
    def exists(self, path: str) -> bool:
        """Check if a file/folder exists"""
        return os.path.exists(self._resolve_path(path))
    
    def read_file(self, path: str) -> Optional[bytes]:
        """Read file content as bytes"""
        try:
            with open(self._resolve_path(path), 'rb') as f:
                return f.read()
        except (IOError, OSError) as e:
            print(f"❌ Error reading file {path}: {e}")
            return None
    
    def read_text(self, path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read file content as text"""
        try:
            with open(self._resolve_path(path), 'r', encoding=encoding) as f:
                return f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            print(f"❌ Error reading text file {path}: {e}")
            return None
    
    def write_file(self, path: str, content: bytes) -> bool:
        """Write bytes to file"""
        try:
            resolved_path = self._resolve_path(path)
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            with open(resolved_path, 'wb') as f:
                f.write(content)
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error writing file {path}: {e}")
            return False
    
    def write_text(self, path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write text to file"""
        try:
            resolved_path = self._resolve_path(path)
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            with open(resolved_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except (IOError, OSError, UnicodeEncodeError) as e:
            print(f"❌ Error writing text file {path}: {e}")
            return False
    
    def list_files(self, folder_path: str, pattern: Optional[str] = None) -> List[str]:
        """List files in a folder, optionally filtered by pattern"""
        try:
            resolved_path = self._resolve_path(folder_path)
            if not os.path.isdir(resolved_path):
                return []
            
            if pattern:
                search_pattern = os.path.join(resolved_path, pattern)
                files = glob.glob(search_pattern)
                return [os.path.basename(f) for f in files if os.path.isfile(f)]
            else:
                return [f for f in os.listdir(resolved_path) 
                       if os.path.isfile(os.path.join(resolved_path, f))]
        except (IOError, OSError) as e:
            print(f"❌ Error listing files in {folder_path}: {e}")
            return []
    
    def download_to_temp(self, path: str, temp_path: str) -> bool:
        """Copy file to temporary location"""
        try:
            resolved_path = self._resolve_path(path)
            if not os.path.exists(resolved_path):
                print(f"❌ Source file {path} does not exist")
                return False
            
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            shutil.copy2(resolved_path, temp_path)
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error copying file {path} to {temp_path}: {e}")
            return False
    
    def upload_from_temp(self, temp_path: str, path: str) -> bool:
        """Copy file from temporary location"""
        try:
            resolved_path = self._resolve_path(path)
            if not os.path.exists(temp_path):
                print(f"❌ Temp file {temp_path} does not exist")
                return False
            
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            shutil.copy2(temp_path, resolved_path)
            return True
        except (IOError, OSError) as e:
            print(f"❌ Error copying file {temp_path} to {path}: {e}")
            return False
    
    def get_provider_name(self) -> str:
        """Get the name of the storage provider"""
        return f"Local File System ({self.base_path})"
