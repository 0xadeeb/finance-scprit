"""
Abstract base class for different output writers.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict


class Writer(ABC):
    """Abstract base class for output writers"""
    
    @abstractmethod
    def write(self, year: str, month: int, transactions_dfs: Dict[str, pd.DataFrame], 
             summary_df: pd.DataFrame, output_path: str) -> bool:
        """Write the financial data to output format"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this writer"""
        pass
    
    @abstractmethod
    def get_writer_name(self) -> str:
        """Get the name of this writer"""
        pass
    
    @abstractmethod
    def supports_formatting(self) -> bool:
        """Check if this writer supports advanced formatting"""
        pass
