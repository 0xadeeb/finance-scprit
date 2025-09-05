"""
CSV file writing functionality.
"""

import pandas as pd
import os
from typing import Dict
from .base import Writer


class CSVWriter(Writer):
    """Handles CSV file writing"""
    
    def get_file_extension(self) -> str:
        """Get the file extension for this writer"""
        return ".csv"
    
    def get_writer_name(self) -> str:
        """Get the name of this writer"""
        return "CSV Writer"
    
    def supports_formatting(self) -> bool:
        """Check if this writer supports advanced formatting"""
        return False
    
    def write(self, year: str, month: int, transactions_dfs: Dict[str, pd.DataFrame], 
             summary_df: pd.DataFrame, output_path: str) -> bool:
        """Write all data to CSV files"""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.splitext(output_path)[0] + "_csv"
            os.makedirs(output_dir, exist_ok=True)
            
            # Write summary data
            summary_file = os.path.join(output_dir, f"summary_{year}.csv")
            summary_df.to_csv(summary_file)
            print(f"✅ Written summary to: {summary_file}")
            
            # Write transaction data for each bank
            for bank_name, transactions_df in transactions_dfs.items():
                trans_file = os.path.join(output_dir, f"{bank_name}_transactions_{year}_{month:02d}.csv")
                transactions_df.to_csv(trans_file, index=False)
                print(f"✅ Written {bank_name} transactions to: {trans_file}")
            
            print(f"✅ All CSV files written to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error writing CSV files: {str(e)}")
            return False
