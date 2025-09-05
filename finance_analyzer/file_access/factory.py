"""
Factory for creating file accessors based on configuration.
"""

from typing import Union
from .base import FileAccessor
from .local_accessor import LocalFileAccessor
from .cloud_accessor import CloudFileAccessor
from ..cloud_storage import CloudStorageFactory


class FileAccessorFactory:
    """Factory for creating appropriate file accessors"""
    
    @staticmethod
    def create_local(base_path: str = ".") -> LocalFileAccessor:
        """Create a local file accessor"""
        return LocalFileAccessor(base_path)
    
    @staticmethod
    def create_cloud(cloud_provider: str) -> CloudFileAccessor:
        """Create a cloud file accessor"""
        cloud_storage = CloudStorageFactory.create(cloud_provider)
        return CloudFileAccessor(cloud_storage)
    
    @staticmethod
    def create_from_config(config) -> FileAccessor:
        """Create file accessor based on configuration"""
        storage_type = getattr(config, 'storage_type', 'cloud')
        
        if storage_type == 'local':
            base_path = getattr(config, 'local_base_path', '.')
            return FileAccessorFactory.create_local(base_path)
        else:
            cloud_provider = getattr(config, 'cloud_provider', 'google_drive')
            return FileAccessorFactory.create_cloud(cloud_provider)
