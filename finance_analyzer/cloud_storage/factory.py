"""
Cloud storage factory for creating different cloud storage providers.
"""

from typing import Dict, Type
from .base import CloudStorage
from .google_drive_api import GoogleDriveAPI


class CloudStorageFactory:
    """Factory for creating cloud storage instances"""
    
    _providers: Dict[str, Type[CloudStorage]] = {
        'google_drive': GoogleDriveAPI,
        'gdrive': GoogleDriveAPI,
        'google': GoogleDriveAPI,
    }
    
    @classmethod
    def create(cls, provider_name: str) -> CloudStorage:
        """Create a cloud storage instance for the specified provider"""
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available_providers = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unsupported cloud storage provider: {provider_name}. "
                f"Available providers: {available_providers}"
            )
        
        provider_class = cls._providers[provider_name]
        return provider_class()
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[CloudStorage]) -> None:
        """Register a new cloud storage provider"""
        cls._providers[name.lower()] = provider_class
        print(f"✅ Registered cloud storage provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available cloud storage providers"""
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_available(cls, provider_name: str) -> bool:
        """Check if a provider is available"""
        return provider_name.lower() in cls._providers
