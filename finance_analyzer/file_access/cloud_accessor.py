"""
Cloud storage file accessor implementation.
"""

from typing import Optional, List
from .base import FileAccessor
from ..cloud_storage import CloudStorage


class CloudFileAccessor(FileAccessor):
    """File accessor for cloud storage providers"""
    
    def __init__(self, cloud_storage: CloudStorage):
        self.cloud_storage = cloud_storage
    
    def exists(self, path: str) -> bool:
        """Check if a file/folder exists in cloud storage"""
        # For cloud storage, we'll try to get file info
        try:
            # This assumes the path is a file ID for cloud storage
            return self.cloud_storage.get_file_info(path) is not None
        except:
            return False
    
    def read_file(self, path: str) -> Optional[bytes]:
        """Read file content as bytes from cloud storage"""
        content = self.cloud_storage.download_content(path)
        if content:
            return content.encode('utf-8') if isinstance(content, str) else content
        return None
    
    def read_text(self, path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read file content as text from cloud storage"""
        return self.cloud_storage.download_content(path)
    
    def write_file(self, path: str, content: bytes) -> bool:
        """Write bytes to cloud storage"""
        # For cloud storage, we need to handle this differently
        # Usually we upload from a local file
        import tempfile
        import os
        
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            result = self.cloud_storage.upload_file(temp_path, path)
            os.unlink(temp_path)
            return result
        except Exception as e:
            print(f"❌ Error writing file to cloud: {e}")
            return False
    
    def write_text(self, path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write text to cloud storage"""
        return self.write_file(path, content.encode(encoding))
    
    def list_files(self, folder_path: str, pattern: Optional[str] = None) -> List[str]:
        """List files in a cloud folder, optionally filtered by pattern"""
        try:
            files = self.cloud_storage.list_files_in_folder(folder_path)
            if pattern:
                import fnmatch
                return [f for f in files if fnmatch.fnmatch(f, pattern)]
            return files
        except Exception as e:
            print(f"❌ Error listing files in cloud folder: {e}")
            return []
    
    def download_to_temp(self, path: str, temp_path: str) -> bool:
        """Download file from cloud to temporary location"""
        return self.cloud_storage.download_file(path, temp_path)
    
    def upload_from_temp(self, temp_path: str, path: str) -> bool:
        """Upload file from temporary location to cloud"""
        return self.cloud_storage.upload_file(temp_path, path)
    
    def get_provider_name(self) -> str:
        """Get the name of the storage provider"""
        return self.cloud_storage.get_provider_name()
    
    def find_file_in_folder(self, folder_id: str, filename: str) -> Optional[str]:
        """Find a file by name in a cloud folder"""
        return self.cloud_storage.find_file_in_folder(folder_id, filename)
