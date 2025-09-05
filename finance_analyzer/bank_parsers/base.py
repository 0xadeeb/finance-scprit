"""
Abstract base class for bank-specific transaction parsing.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Tuple, Dict


class Bank(ABC):
    """Abstract base class for bank-specific transaction processing"""
    
    def __init__(self, name: str, skiprows: int, date_col: str, description_col: str, debit_col: str, credit_col: str):
        self.name = name
        self.skiprows = skiprows
        self.date_col = date_col
        self.description_col = description_col
        self.credit_col = credit_col
        self.debit_col = debit_col
    
    @abstractmethod
    def parse_transaction(self, transaction_details: pd.Series) -> Tuple[str, str]:
        """Parse transaction to extract category and merchant information"""
        pass
    
    def get_column_mapping(self) -> Dict[str, str]:
        """Get the column name mapping for standardization"""
        return {
            self.date_col: 'Date',
            self.description_col: 'Description',
            self.credit_col: 'Credit',
            self.debit_col: 'Debit'
        }
