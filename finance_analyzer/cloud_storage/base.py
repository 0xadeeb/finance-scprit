"""
Abstract cloud storage interface for file operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class CloudStorage(ABC):
    """Abstract base class for cloud storage providers"""
    
    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the cloud storage provider"""
        pass
    
    @abstractmethod
    def download_content(self, file_id: str) -> Optional[str]:
        """Download file content directly as string"""
        pass
    
    @abstractmethod
    def download_file(self, file_id: str, local_path: str) -> bool:
        """Download a file from cloud storage to local path"""
        pass
    
    @abstractmethod
    def upload_content(self, content: str, file_id: str, mimetype: str = 'application/json') -> bool:
        """Upload content directly to a file in cloud storage"""
        pass
    
    @abstractmethod
    def upload_file(self, local_path: str, file_id: str) -> bool:
        """Upload/update a local file to cloud storage"""
        pass
    
    @abstractmethod
    def create_file(self, filename: str, content: str, parent_folder_id: str, mimetype: str = 'application/json') -> Optional[str]:
        """Create a new file in cloud storage"""
        pass
    
    @abstractmethod
    def find_file_in_folder(self, folder_id: str, filename: str) -> Optional[str]:
        """Find a file by name in a specific folder"""
        pass
    
    @abstractmethod
    def list_files_in_folder(self, folder_id: str) -> Optional[list]:
        """List all files in a folder (optional method for future use)"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the cloud storage provider"""
        pass
