"""
Finance Analyzer - A tool for analyzing bank statements and generating financial summaries
using cloud storage APIs for file management.
"""

__version__ = "1.0.0"
__author__ = "Finance Analyzer Team"

from .main import FinanceAnalyzer
from .cloud_storage import CloudStorageFactory
from .file_access import FileAccessorFactory
from . import models

__all__ = [
    "FinanceAnalyzer",
    "CloudStorageFactory",
    "FileAccessorFactory",
    "models"
]
