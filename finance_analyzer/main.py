"""
Main application class that orchestrates the finance analysis process.
"""

import os
import signal
import sys
import calendar
import pandas as pd
from typing import Dict, List
import glob
import shutil

from .cloud_storage import CloudStorageFactory
from .bank_parsers import BankParserRegistry
from .writers import WriterFactory
from .config_manager import ConfigManager
from .transaction_processor import TransactionProcessor
from .file_access import FileAccessorFactory
from .constants import (
    TEMP_DIR, LOCAL_OUTPUT_FILE, CATEGORIES, CAT_MAPPING, 
    BANK_ACCOUNTS, CREDIT_CATEGORIES, DEBIT_CATEGORIES, 
    NET_CATEGORIES, BALANCE_ROWS
)


class FinanceAnalyzer:
    """Main application class for finance analysis"""
    
    def __init__(self):
        self.config = None
        self.file_accessor = None
        self.transaction_processor = None
        self.writer = None
        self.temp_files_created: List[str] = []
        self.cleanup_registered = False
        
    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful cleanup"""
        if not self.cleanup_registered:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self.cleanup_registered = True
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals (Ctrl+C) and cleanup"""
        print(f"\n\n🛑 Received signal {signum}")
        print("🧹 Cleaning up temporary files before exit...")
        self._comprehensive_cleanup()
        print("✅ Cleanup complete. Goodbye!")
        sys.exit(0)
    
    def _track_temp_file(self, filepath: str) -> None:
        """Track a temporary file for cleanup"""
        if filepath and filepath not in self.temp_files_created:
            self.temp_files_created.append(filepath)
        
    def setup(self) -> None:
        """Initialize all components"""
        print("🏦 Finance Script - Multi-Storage Finance Analyzer")
        print("=" * 50)
        
        # Register signal handlers for graceful cleanup
        self._register_signal_handlers()
        
        # Setup temp directory
        self._setup_temp_directory()
        
        # Initialize components
        self.config = ConfigManager()
        self.file_accessor = FileAccessorFactory.create_from_config(self.config)
        self.transaction_processor = TransactionProcessor(self.file_accessor, self._track_temp_file)
        self.writer = WriterFactory.create('excel')
        
        print(f"✅ Setup complete using {self.file_accessor.get_provider_name()}")
        print("💡 Press Ctrl+C at any time to safely exit and cleanup temporary files")
    
    def _setup_temp_directory(self) -> None:
        """Create temporary directory if it doesn't exist"""
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            print(f"✅ Created temp directory: {TEMP_DIR}")
    
    def _get_user_input(self) -> tuple:
        """Get month and year from user with proper interrupt handling"""
        try:
            month = int(input("\n📅 Enter the month (1-12): "))
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
                
            year = input("📅 Enter the year (default 2024): ").strip() or "2024"
            
            # Basic validation for year
            year_int = int(year)
            if year_int < 2000 or year_int > 2030:
                print("⚠️  Warning: Year seems unusual, but continuing...")
                
            return month, year
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Input cancelled by user")
            self._comprehensive_cleanup()
            print("✅ Cleanup complete. Goodbye!")
            sys.exit(0)
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            return self._get_user_input()  # Retry
    
    def _download_finance_file(self) -> None:
        """Download the Finance.xlsx file from storage"""
        print(f"\n📥 Downloading files from {self.file_accessor.get_provider_name()}...")
        
        # Track the main output file
        self._track_temp_file(LOCAL_OUTPUT_FILE)
        
        if not self.file_accessor.download_to_temp(self.config.finance_file_id, LOCAL_OUTPUT_FILE):
            raise Exception("Failed to download Finance.xlsx file")
    
    def _process_bank_transactions(self, year: str, month: int) -> Dict[str, int]:
        """Process transactions for all banks"""
        print(f"\n💳 Processing bank statements...")
        
        category_sums = {category: 0 for category in CATEGORIES}
        transactions_dfs = {}
        
        # Setup category mappings
        for item in CATEGORIES:
            CAT_MAPPING[item.lower()] = item.title()
        
        for bank_name in BANK_ACCOUNTS:
            try:
                print(f"\nProcessing {bank_name}...")
                
                # Read transactions from cloud storage
                transactions_df = self.transaction_processor.read_transactions_df(
                    bank_name, year, month, self.config.bank_folder_id
                )

                # Process each transaction
                for i, row in transactions_df.iterrows():
                    amount = row['Debit'] if pd.notna(row['Debit']) else row['Credit']
                    if pd.notna(row['Debit']):
                        amount = -amount

                    if pd.isna(amount):
                        transactions_df = transactions_df.iloc[:i]
                        break

                    # Create a copy of the row with the amount for categorization
                    transaction_row = row.copy()
                    transaction_row['Amount'] = amount

                    category = self.transaction_processor.categorise_transaction(bank_name, transaction_row)
                    transactions_df.loc[i, 'Category'] = category
                    category_sums[category] += amount

                transactions_dfs[bank_name] = transactions_df
                print(f"✅ Processed {len(transactions_df)} transactions from {bank_name}")
                
            except FileNotFoundError as e:
                print(f"⚠️  Skipping {bank_name}: {str(e)}")
                continue
            except Exception as e:
                print(f"❌ Error processing {bank_name}: {str(e)}")
                continue
        
        return category_sums, transactions_dfs
    
    def _update_summary(self, year: str, month: int, category_sums: Dict[str, int]) -> pd.DataFrame:
        """Update the summary DataFrame with new data"""
        print(f"\n📈 Generating summary...")
        
        # Load existing summary
        with pd.ExcelFile(LOCAL_OUTPUT_FILE, engine='openpyxl') as xls:
            summary_df = pd.read_excel(xls, year, index_col=0)

        # Update summary with new data
        for category, total in category_sums.items():
            summary_df.loc[category, calendar.month_name[month]] = total

        monthly_columns = [calendar.month_name[i + 1] for i in range(12)]

        # Calculate totals
        summary_df.loc['Total Credit', calendar.month_name[month]] = sum([
            summary_df.loc[category, calendar.month_name[month]] for category in CREDIT_CATEGORIES
        ])
        summary_df.loc['Total Debit', calendar.month_name[month]] = sum([
            summary_df.loc[category, calendar.month_name[month]] for category in DEBIT_CATEGORIES
        ])
        summary_df.loc['Total NET', calendar.month_name[month]] = sum([
            summary_df.loc[category, calendar.month_name[month]] for category in NET_CATEGORIES
        ])
        
        # Calculate averages and totals
        summary_df['Avg'] = summary_df[monthly_columns].mean(axis=1).round(2)
        summary_df['Total'] = summary_df[monthly_columns].sum(axis=1).round(2) - summary_df['Avg']
        
        # Update balances
        summary_df.loc['Closing Bank Bal.', calendar.month_name[month]] = (
            summary_df.loc['Opening Bank Bal.', calendar.month_name[month]] + 
            summary_df.loc['Total Credit', calendar.month_name[month]] + 
            summary_df.loc['Total Debit', calendar.month_name[month]]
        )
        summary_df.loc['Closing In Hand', calendar.month_name[month]] = (
            summary_df.loc['Opening In Hand', calendar.month_name[month]]
        )

        # Update next month's opening balances
        if month != 12:
            summary_df.loc['Opening Bank Bal.', calendar.month_name[month + 1]] = (
                summary_df.loc['Closing Bank Bal.', calendar.month_name[month]]
            )
            summary_df.loc['Opening In Hand', calendar.month_name[month + 1]] = (
                summary_df.loc['Closing In Hand', calendar.month_name[month]]
            )

        # Reorder rows
        ordered_rows = (
            BALANCE_ROWS[:2] + CREDIT_CATEGORIES + ["Total Credit"] + 
            DEBIT_CATEGORIES + ["Total Debit"] + NET_CATEGORIES + 
            ["Total NET"] + BALANCE_ROWS[2:]
        )

        if len(summary_df) != len(ordered_rows):
            print("❌ Summary DataFrame structure mismatch")
            print(f"Expected rows: {len(ordered_rows)}")
            print(f"Actual rows: {len(summary_df)}")
            print(f"Actual index: {summary_df.index.values}")
            raise Exception("Summary DataFrame structure mismatch")

        summary_df = summary_df.reindex(ordered_rows)
        return summary_df
    
    def _upload_results(self) -> None:
        """Upload results back to storage"""
        print(f"\n📤 Uploading updated files to {self.file_accessor.get_provider_name()}...")
        
        # Upload Finance.xlsx back to storage
        self.file_accessor.upload_from_temp(LOCAL_OUTPUT_FILE, self.config.finance_file_id)
    
    def _cleanup(self) -> None:
        """Clean up temporary files"""
        self._comprehensive_cleanup()
    
    def _comprehensive_cleanup(self) -> None:
        """Comprehensive cleanup of all temporary files and directories"""
        cleaned_files = []
        
        # Clean tracked temporary files
        for temp_file in self.temp_files_created:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    cleaned_files.append(os.path.basename(temp_file))
                except Exception as e:
                    print(f"⚠️  Warning: Could not remove {temp_file}: {e}")
        
        # Clean up temp directory and all its contents
        if os.path.exists(TEMP_DIR):
            try:
                # Find all files in temp directory
                temp_files = glob.glob(os.path.join(TEMP_DIR, "*"))
                for temp_file in temp_files:
                    if os.path.isfile(temp_file):
                        try:
                            os.remove(temp_file)
                            cleaned_files.append(os.path.basename(temp_file))
                        except Exception as e:
                            print(f"⚠️  Warning: Could not remove {temp_file}: {e}")
                
                # Try to remove the temp directory if empty
                try:
                    if not os.listdir(TEMP_DIR):
                        shutil.rmtree(TEMP_DIR)
                    else:
                        print(f"⚠️  Temp directory {TEMP_DIR} not empty after cleanup")
                except Exception as e:
                    print(f"⚠️  Could not remove temp directory: {e}")
                    
            except Exception as e:
                print(f"⚠️  Error cleaning temp directory: {e}")
        
        # Clean up any stray temporary files created by tempfile module
        try:
            import tempfile
            temp_prefix = tempfile.gettempdir()
            # Look for files matching our patterns
            patterns = [
                os.path.join(temp_prefix, "*_*_Bankstatement*.xlsx"),
                os.path.join(temp_prefix, "tmp*_merchant_category.json"), 
                os.path.join(temp_prefix, "tmp*.json")
            ]
            
            for pattern in patterns:
                for temp_file in glob.glob(pattern):
                    try:
                        # Only remove if it's relatively recent (less than 1 day old)
                        import time
                        if time.time() - os.path.getctime(temp_file) < 86400:  # 24 hours
                            os.remove(temp_file)
                            cleaned_files.append(os.path.basename(temp_file))
                    except Exception:
                        pass  # Ignore errors for system temp files
        except Exception:
            pass  # Ignore if we can't clean system temp files
        
        if cleaned_files:
            print(f"🧹 Cleaned up temporary files: {', '.join(set(cleaned_files))}")
        else:
            print("🧹 No temporary files to clean up")
        
        # Clear the tracking list
        self.temp_files_created.clear()
    
    def run(self) -> None:
        """Run the main application"""
        try:
            # Setup
            self.setup()
            
            # Get user input
            month, year = self._get_user_input()
            print(f"\n📊 Processing data for {calendar.month_name[month]} {year}")
            
            # Download finance file
            self._download_finance_file()
            
            # Load merchant category mappings
            self.transaction_processor.manage_merchant_category_file(self.config.bank_folder_id)
            
            # Process transactions
            category_sums, transactions_dfs = self._process_bank_transactions(year, month)
            
            # Save merchant category mappings
            self.transaction_processor.save_merchant_category_file(self.config.bank_folder_id)
            
            # Update summary
            summary_df = self._update_summary(year, month, category_sums)
            
            # Write to Excel
            print(f"💾 Saving results to Excel...")
            self.writer.write(year, month, transactions_dfs, summary_df, LOCAL_OUTPUT_FILE)
            
            # Upload results
            self._upload_results()
            
            # Success message
            print(f"\n✅ Processing complete! Summary for {calendar.month_name[month]} {year} has been updated.")
            print(f"📊 Processed {sum(len(df) for df in transactions_dfs.values())} total transactions")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise
        finally:
            # Cleanup
            self._cleanup()
