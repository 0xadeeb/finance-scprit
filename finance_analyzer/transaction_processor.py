"""Transaction processing and categorization logic (domain-focused).

This class now operates purely on domain `Transaction` objects. All I/O,
DataFrame handling, and interactive prompting have moved to the orchestrator
layer (`FinanceAnalyzer`). Legacy DataFrame + prompt based methods have been
removed to keep the core clean.
"""

from typing import Dict, Tuple, List

from .constants import CAT_MAPPING
from .bank_parsers import BankParserRegistry
from .file_access import FileAccessor
from .services.merchant_mapping_store import MerchantMappingStore
from .models import Transaction, CategorizationRequest


class TransactionProcessor:
    """Handles transaction processing and categorization"""
    
    def __init__(self, file_accessor: FileAccessor, temp_file_tracker=None, merchant_store: MerchantMappingStore | None = None):
        self.file_accessor = file_accessor
        self.temp_file_tracker = temp_file_tracker
        self.merchant_store = merchant_store or MerchantMappingStore(file_accessor, temp_file_tracker)
        self.merchant_category_dict: Dict[str, str] = {}

    def manage_merchant_category_file(self, bank_folder_id: str) -> None:
        self.merchant_category_dict = self.merchant_store.load(bank_folder_id)

    def save_merchant_category_file(self, bank_folder_id: str) -> bool:
        return self.merchant_store.save(bank_folder_id, self.merchant_category_dict)
    
    def categorize_transactions(
        self,
        bank_name: str,
        transactions: List[Transaction],
    ) -> Tuple[List[Transaction], Dict[str, str], List[CategorizationRequest]]:
        """Assign categories/merchants where possible without user interaction.

        Returns (transactions, merchant_mapping, pending_requests).
        """
        bank = BankParserRegistry.get_bank(bank_name.lower())
        pending: List[CategorizationRequest] = []

        for tx in transactions:
            if bank:
                raw_category, merchant = bank.parse_transaction(tx)
                if merchant:
                    tx.merchant = merchant
                if raw_category:
                    normalized = CAT_MAPPING.get(raw_category.lower())
                    if normalized:
                        tx.category = normalized

            # Merchant mapping application
            if not tx.category and tx.merchant and tx.merchant in self.merchant_category_dict:
                tx.category = self.merchant_category_dict[tx.merchant]

            if not tx.category:
                pending.append(CategorizationRequest(transaction_id=tx.id, transaction=tx))

        return transactions, self.merchant_category_dict, pending
