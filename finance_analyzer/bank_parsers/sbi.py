"""
SBI Bank specific transaction processing.
"""

import pandas as pd
import re
from typing import Tuple
from .base import Bank


class SBIBank(Bank):
    """SBI Bank specific transaction processing"""
    
    def __init__(self):
        super().__init__('SBI', 19, 'Txn Date', 'Description', 'Debit', 'Credit')
        # Regex pattern for UPI transactions
        self.upi_pattern = re.compile(r"^.*?UPI\/(?:CR|DR)\/\d{12}\/([^/]+)\/([^/]+)\/([^/]+)\/(.+?)--$")
    
    def parse_transaction(self, transaction_details: pd.Series) -> Tuple[str, str]:
        """Parse SBI transaction details"""
        description = transaction_details['Description'].upper()
        category = None
        merchant = None
        
        # UPI Transactions: Use regex pattern
        match = self.upi_pattern.match(description)
        if match:
            merchant_name = match.group(1).strip()
            bank_handle = match.group(2).strip()
            vpa_username = match.group(3).strip()
            category = match.group(4).strip().lower()
            
            # Create a robust, unique merchant ID
            merchant = f"{merchant_name}|{bank_handle}|{vpa_username}"
            
            return category, merchant

        return category, merchant
