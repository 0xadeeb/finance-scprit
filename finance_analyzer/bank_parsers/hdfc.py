"""
HDFC Bank specific transaction processing.
"""

import pandas as pd
import re
from typing import Tuple
from .base import Bank


class HDFCBank(Bank):
    """HDFC Bank specific transaction processing"""
    
    def __init__(self):
        super().__init__('HDFC', 20, 'Date', 'Narration', 'Withdrawal Amt.', 'Deposit Amt.')
        # Regex pattern for UPI transactions: UPI-<merchant_name>-<merchant_id>-<12_digit_txn_id>-<category>
        self.upi_pattern = re.compile(r"^UPI-(.*?)-(.*?)-\d{12}-(.+)$")
    
    def parse_transaction(self, transaction_details: pd.Series) -> Tuple[str, str]:
        """Parse HDFC transaction details using regex for UPI transactions"""
        description = transaction_details['Description']
        original_desc = description
        description = description.upper().strip()
        
        category = None
        merchant = None
        
        # UPI Transactions: Use regex pattern
        if description.startswith('UPI'):
            match = self.upi_pattern.match(description)
            if match:
                merchant_name = match.group(1).strip()
                merchant_id = match.group(2).strip()
                merchant = f"{merchant_name}|{merchant_id}"
                category = match.group(3).strip().lower()
        
        return category, merchant