"""
Transaction processing and categorization logic.
"""

import os
import json
import calendar
import pandas as pd
from typing import Dict, Any, Tuple, Optional

from .constants import CATEGORIES, CAT_MAPPING, TEMP_DIR
from .bank_parsers import BankParserRegistry
from .file_access import FileAccessor


class TransactionProcessor:
    """Handles transaction processing and categorization"""
    
    def __init__(self, file_accessor: FileAccessor, temp_file_tracker=None):
        self.file_accessor = file_accessor
        self.merchant_category_dict = {}
        self.merchant_file_id = None
        self.temp_file_tracker = temp_file_tracker
    
    def manage_merchant_category_file(self, bank_folder_id: str) -> None:
        """Load or create merchant category mappings"""
        filename = 'merchant_category.json'
        
        # For cloud storage, we need to find the file in the folder
        # For local storage, we use the folder path + filename
        if hasattr(self.file_accessor, 'find_file_in_folder'):
            # Cloud storage - find file by name in folder
            file_id = self.file_accessor.find_file_in_folder(bank_folder_id, filename)
            if file_id:
                print(f"📄 Found existing {filename} (File ID: {file_id})")
                print(f"🔍 Searching in folder ID: {bank_folder_id}")
                content = self.file_accessor.read_text(file_id)
                if content:
                    try:
                        self.merchant_category_dict = json.loads(content)
                        print(f"✅ Loaded {len(self.merchant_category_dict)} merchant-category mappings")
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parsing {filename}: {str(e)}. Starting with empty dict.")
                        self.merchant_category_dict = {}
                else:
                    print(f"⚠️  Failed to download {filename}. Starting with empty dict.")
                    self.merchant_category_dict = {}
                self.merchant_file_id = file_id
            else:
                print(f"📄 {filename} not found in Bank folder, will create it")
                self.merchant_category_dict = {}
                self.merchant_file_id = None
        else:
            # Local storage - use folder path + filename
            file_path = f"{bank_folder_id}/{filename}"
            if self.file_accessor.exists(file_path):
                print(f"📄 Found existing {filename}")
                content = self.file_accessor.read_text(file_path)
                if content:
                    try:
                        self.merchant_category_dict = json.loads(content)
                        print(f"✅ Loaded {len(self.merchant_category_dict)} merchant-category mappings")
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parsing {filename}: {str(e)}. Starting with empty dict.")
                        self.merchant_category_dict = {}
                else:
                    print(f"⚠️  Failed to read {filename}. Starting with empty dict.")
                    self.merchant_category_dict = {}
                self.merchant_file_id = file_path
            else:
                print(f"📄 {filename} not found in Bank folder, will create it")
                self.merchant_category_dict = {}
                self.merchant_file_id = f"{bank_folder_id}/{filename}"
    
    def save_merchant_category_file(self, bank_folder_id: str) -> bool:
        """Save merchant category dictionary to storage"""
        if not self.merchant_category_dict:
            return True  # Nothing to save
        
        filename = 'merchant_category.json'
        content = json.dumps(self.merchant_category_dict, indent=2)
        
        if self.merchant_file_id:
            # Update existing file
            success = self.file_accessor.write_text(self.merchant_file_id, content)
            if success:
                print(f"✅ Updated {filename} with {len(self.merchant_category_dict)} mappings")
            return success
        else:
            # Create new file
            if hasattr(self.file_accessor, 'find_file_in_folder'):
                # Cloud storage - need to create and get new file ID
                # This is a limitation - cloud storage APIs typically don't support direct content upload
                # We'd need to create a temp file and upload it
                import tempfile
                import os
                
                try:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                        temp_file.write(content)
                        temp_path = temp_file.name
                    
                    # Track the temp file for cleanup
                    if self.temp_file_tracker:
                        self.temp_file_tracker(temp_path)
                    
                    success = self.file_accessor.upload_from_temp(temp_path, f"{bank_folder_id}/{filename}")
                    
                    # Clean up immediately after upload
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass  # If immediate cleanup fails, the tracker will handle it
                    
                    if success:
                        # Try to get the new file ID
                        new_file_id = self.file_accessor.find_file_in_folder(bank_folder_id, filename)
                        if new_file_id:
                            self.merchant_file_id = new_file_id
                            print(f"✅ Created {filename} with {len(self.merchant_category_dict)} mappings")
                            return True
                    return False
                except Exception as e:
                    print(f"❌ Error creating {filename}: {e}")
                    return False
            else:
                # Local storage - direct write
                file_path = f"{bank_folder_id}/{filename}"
                success = self.file_accessor.write_text(file_path, content)
                if success:
                    self.merchant_file_id = file_path
                    print(f"✅ Created {filename} with {len(self.merchant_category_dict)} mappings")
                return success
    
    def parse_transaction(self, bank_name: str, transaction_details: pd.Series) -> Tuple[str, str]:
        """Parse transaction details using the appropriate bank parser"""
        bank_instance = BankParserRegistry.get_bank(bank_name.lower())
        
        if bank_instance:
            return bank_instance.parse_transaction(transaction_details)
        else:
            return None, None
    
    def prompt_user_for_category(self, transaction_details: Dict[str, Any]) -> Tuple[str, bool]:
        # return "Misl", False
        """Prompt user to categorize a transaction"""
        print(f"Transaction details:")
        print(f"Date: {transaction_details['Date']}")
        print(f"Description: {transaction_details['Description']}")
        print(f"Amount: {transaction_details['Amount']}")
        print("Please select a category:")

        num_categories = len(CATEGORIES)
        for i in range(0, num_categories, 4):
            row = []
            for j in range(i, min(i + 4, num_categories)):
                row.append(f"{j+1}. {CATEGORIES[j].title()}")
            print("{:<25} {:<25} {:<25} {:<25}".format(*row, *([""]*(4-len(row)))))

        while True:
            try:
                selected_index = int(input("\nEnter the number corresponding to the category: ")) - 1
                if selected_index < 0 or selected_index >= num_categories:
                    print("Invalid selection. Please select a number corresponding to the category.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        while True:
            store_mapping = input("Do you want to remember this merchant-category mapping? (y/[n]): ").lower()
            if store_mapping not in ['y', 'n', '']:
                print("Invalid input. Please enter 'y' or 'n'.")
            else:
                store_mapping = store_mapping == 'y'
                break

        print()
        return CATEGORIES[selected_index], store_mapping
    
    def categorise_transaction(self, bank_name: str, transaction_details: pd.Series) -> str:
        """Categorize a transaction based on bank-specific parsing and user input"""
        category, merchant = self.parse_transaction(bank_name, transaction_details)

        if category and category in CAT_MAPPING:
            return CAT_MAPPING[category]

        if not merchant or merchant not in self.merchant_category_dict:
            category = None
        else:
            category = self.merchant_category_dict[merchant]
            if category in CATEGORIES:
                return category
            else:
                del self.merchant_category_dict[merchant]
                category = None

        # Create transaction details dict for user prompt
        transaction_info = {
            'Date': transaction_details['Date'],
            'Description': transaction_details['Description'],
            'Amount': transaction_details.get('Amount', 0)
        }
        
        category, store_mapping = self.prompt_user_for_category(transaction_info)
        if merchant and store_mapping:
            self.merchant_category_dict[merchant] = category

        return category
    
    def read_transactions_df(self, bank_name: str, year: str, month: int, bank_folder_id: str) -> pd.DataFrame:
        """Read transactions from storage and return DataFrame"""
        filename = f"Bankstatement{calendar.month_abbr[month]}.xlsx"
        
        if hasattr(self.file_accessor, 'find_file_in_folder'):
            # Cloud storage - navigate through folder hierarchy
            # Find bank folder
            bank_folder_id = self.file_accessor.find_file_in_folder(bank_folder_id, bank_name)
            if not bank_folder_id:
                raise FileNotFoundError(f"Bank folder '{bank_name}' not found in cloud storage")
            
            # Find year folder
            year_folder_id = self.file_accessor.find_file_in_folder(bank_folder_id, year)
            if not year_folder_id:
                raise FileNotFoundError(f"Year folder '{year}' not found in bank folder '{bank_name}'")
            
            # Find the specific bank statement file
            file_id = self.file_accessor.find_file_in_folder(year_folder_id, filename)
            if not file_id:
                raise FileNotFoundError(f"File '{filename}' not found in {bank_name}/{year}")
            
            file_path = file_id
        else:
            # Local storage - construct path
            file_path = f"{bank_folder_id}/{bank_name}/{year}/{filename}"
            if not self.file_accessor.exists(file_path):
                raise FileNotFoundError(f"File '{file_path}' not found")
        
        # Download/copy the file to temporary location for pandas processing
        temp_file = os.path.join(TEMP_DIR, f"{bank_name}_{year}_{filename}")
        
        # Track the temp file for cleanup
        if self.temp_file_tracker:
            self.temp_file_tracker(temp_file)
            
        if not self.file_accessor.download_to_temp(file_path, temp_file):
            raise Exception(f"Failed to download {filename}")
        
        # Get bank instance and process the file
        bank_instance = BankParserRegistry.get_bank(bank_name.lower())
        if not bank_instance:
            raise ValueError(f"Unknown bank: {bank_name}")
        
        name_mapping = bank_instance.get_column_mapping()
        
        transactions_df = pd.read_excel(temp_file, skiprows=bank_instance.skiprows)
        transactions_df['Category'] = pd.NA
        transactions_df.rename(name_mapping, axis='columns', inplace=True)
        
        # Parse dates with explicit handling for common formats
        transactions_df['Date'] = pd.to_datetime(
            transactions_df['Date'], 
            errors='coerce', 
            dayfirst=True,
            format='mixed'  # Allows pandas to handle multiple date formats
        )
        transactions_df['Date'] = transactions_df['Date'].dt.strftime('%d %b %Y')
        transactions_df = transactions_df[["Date", "Description", "Credit", "Debit", 'Category']]
        
        # Clean up temp file immediately
        try:
            os.remove(temp_file)
        except Exception:
            pass  # If immediate cleanup fails, the tracker will handle it
        
        return transactions_df
