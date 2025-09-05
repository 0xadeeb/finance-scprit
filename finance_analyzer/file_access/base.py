"""
Abstract file access layer for both local and cloud storage.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import io


class FileAccessor(ABC):
    """Abstract base class for file access operations"""
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a file/folder exists"""
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> Optional[bytes]:
        """Read file content as bytes"""
        pass
    
    @abstractmethod
    def read_text(self, path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read file content as text"""
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: bytes) -> bool:
        """Write bytes to file"""
        pass
    
    @abstractmethod
    def write_text(self, path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write text to file"""
        pass
    
    @abstractmethod
    def list_files(self, folder_path: str, pattern: Optional[str] = None) -> List[str]:
        """List files in a folder, optionally filtered by pattern"""
        pass
    
    @abstractmethod
    def download_to_temp(self, path: str, temp_path: str) -> bool:
        """Download/copy file to temporary location"""
        pass
    
    @abstractmethod
    def upload_from_temp(self, temp_path: str, path: str) -> bool:
        """Upload/copy file from temporary location"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the storage provider"""
        pass
    
    def read_excel_file(self, path: str, temp_dir: str = './temp') -> Optional[str]:
        """Helper method to download Excel file for pandas processing"""
        import os
        import tempfile
        
        # Generate temp file path
        temp_path = os.path.join(temp_dir, f"temp_{hash(path)}.xlsx")
        
        if self.download_to_temp(path, temp_path):
            return temp_path
        return None
    
    def cleanup_temp_file(self, temp_path: str) -> None:
        """Helper method to clean up temporary files"""
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
