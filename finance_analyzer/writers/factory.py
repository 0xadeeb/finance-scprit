"""
Writer factory for creating different output writers.
"""

from typing import Dict, Type
from .base import Writer
from .excel_writer import ExcelWriter
from .csv_writer import CSVWriter
from .json_writer import JSONWriter


class WriterFactory:
    """Factory for creating writer instances"""
    
    _writers: Dict[str, Type[Writer]] = {
        'excel': ExcelWriter,
        'xlsx': ExcelWriter,
        'csv': CSVWriter,
        'json': JSONWriter,
    }
    
    @classmethod
    def create(cls, writer_type: str) -> Writer:
        """Create a writer instance for the specified type"""
        writer_type = writer_type.lower()
        
        if writer_type not in cls._writers:
            available_writers = ', '.join(cls._writers.keys())
            raise ValueError(
                f"Unsupported writer type: {writer_type}. "
                f"Available writers: {available_writers}"
            )
        
        writer_class = cls._writers[writer_type]
        return writer_class()
    
    @classmethod
    def register_writer(cls, name: str, writer_class: Type[Writer]) -> None:
        """Register a new writer type"""
        cls._writers[name.lower()] = writer_class
        print(f"✅ Registered writer: {name}")
    
    @classmethod
    def get_available_writers(cls) -> list:
        """Get list of available writer types"""
        return list(cls._writers.keys())
    
    @classmethod
    def is_writer_available(cls, writer_type: str) -> bool:
        """Check if a writer type is available"""
        return writer_type.lower() in cls._writers
