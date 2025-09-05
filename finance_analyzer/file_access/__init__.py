"""
File access abstraction layer.
"""

from .base import FileAccessor
from .local_accessor import LocalFileAccessor
from .cloud_accessor import CloudFileAccessor
from .factory import FileAccessorFactory

__all__ = [
    "FileAccessor",
    "LocalFileAccessor", 
    "CloudFileAccessor",
    "FileAccessorFactory"
]
