"""
JSON file writing functionality.
"""

import pandas as pd
import json
import os
from typing import Dict
from .base import Writer


class JSONWriter(Writer):
    """Handles JSON file writing"""
    
    def get_file_extension(self) -> str:
        """Get the file extension for this writer"""
        return ".json"
    
    def get_writer_name(self) -> str:
        """Get the name of this writer"""
        return "JSON Writer"
    
    def supports_formatting(self) -> bool:
        """Check if this writer supports advanced formatting"""
        return False
    
    def write(self, year: str, month: int, transactions_dfs: Dict[str, pd.DataFrame], 
             summary_df: pd.DataFrame, output_path: str) -> bool:
        """Write all data to JSON files"""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.splitext(output_path)[0] + "_json"
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert summary DataFrame to JSON
            summary_dict = summary_df.to_dict('index')
            summary_file = os.path.join(output_dir, f"summary_{year}.json")
            with open(summary_file, 'w') as f:
                json.dump(summary_dict, f, indent=2, default=str)
            print(f"✅ Written summary to: {summary_file}")
            
            # Write transaction data for each bank
            transactions_data = {}
            for bank_name, transactions_df in transactions_dfs.items():
                # Convert DataFrame to records format
                transactions_data[bank_name] = transactions_df.to_dict('records')
            
            trans_file = os.path.join(output_dir, f"transactions_{year}_{month:02d}.json")
            with open(trans_file, 'w') as f:
                json.dump(transactions_data, f, indent=2, default=str)
            print(f"✅ Written all transactions to: {trans_file}")
            
            print(f"✅ All JSON files written to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error writing JSON files: {str(e)}")
            return False
