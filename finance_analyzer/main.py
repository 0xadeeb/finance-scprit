"""
Main application class that orchestrates the finance analysis process.
"""

import os
import signal
import sys
import calendar
from typing import Dict, List
import glob
import shutil
import asyncio

from .cloud_storage import CloudStorageFactory
from .writers import WriterFactory
from .config_manager import ConfigManager
from .transaction_processor import TransactionProcessor
from .services.merchant_mapping_store import MerchantMappingStore
from .statement_readers import StatementReaderFactory
from .models import Transaction
from .file_access import FileAccessorFactory
from .constants import (
    TEMP_DIR, LOCAL_OUTPUT_FILE, CATEGORIES, CAT_MAPPING,
    BANK_ACCOUNTS
)
from .services.summary.service import SummaryService
from .interaction.cli_async_port import CliAsyncInteractionPort
from .interaction.port import (
    CategorizationItem, CategorizationDecision, CashEntry, SummaryView,
    SummaryCategoryLine
)
from .interaction.presenters import build_summary_view
from .categorization_strategy import (
    CategorizationMode, CategorizationStrategy, UserPromptStrategy, AutoStrategy
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
        self.summary_service = SummaryService()
        self.statement_reader = None
        # Interaction port (set in setup to allow swapping implementations later)
        self.interaction_port = None
        
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
        merchant_store = MerchantMappingStore(self.file_accessor, self._track_temp_file)
        self.transaction_processor = TransactionProcessor(
            self.file_accessor, self._track_temp_file, merchant_store=merchant_store
        )
        # Statement reader (format decided by config)
        self.statement_reader = StatementReaderFactory.create(self.config, self.file_accessor, self._track_temp_file)
        self.writer = WriterFactory.create('excel')
        # Interaction port (CLI implementation; future GUI can swap here)
        self.interaction_port = CliAsyncInteractionPort()
        
        print(f"✅ Setup complete using {self.file_accessor.get_provider_name()}")
        print("💡 Press Ctrl+C at any time to safely exit and cleanup temporary files")
    
    def _setup_temp_directory(self) -> None:
        """Create temporary directory if it doesn't exist"""
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            print(f"✅ Created temp directory: {TEMP_DIR}")
    
    # Legacy direct input removed; month/year now obtained via interaction port (async)
    async def _get_initial_context(self):
        return await self.interaction_port.request_initial_context()
    
    def _download_finance_file(self) -> None:
        """Download the Finance.xlsx file from storage"""
        print(f"\n📥 Downloading files from {self.file_accessor.get_provider_name()}...")
        
        # Track the main output file
        self._track_temp_file(LOCAL_OUTPUT_FILE)
        
        if not self.file_accessor.download_to_temp(self.config.finance_file_id, LOCAL_OUTPUT_FILE):
            raise Exception("Failed to download Finance.xlsx file")
    
    # Helper removed (direct awaiting of returned futures now used)

    def _apply_categorization_decisions(self, pending, decisions: List[CategorizationDecision]):
        for d in decisions:
            if d.idx < 0 or d.idx >= len(pending):
                continue
            tx = pending[d.idx].transaction
            tx.category = d.category
            if d.remember_mapping and tx.merchant and tx.merchant not in self.transaction_processor.merchant_category_dict:
                self.transaction_processor.merchant_category_dict[tx.merchant] = d.category
                self.transaction_processor.merchant_store.mark_dirty()

    def _integrate_cash_entries(self, cash_entries: List[CashEntry], category_sums, transactions_by_bank):
        if not cash_entries:
            return
        txs: List[Transaction] = []
        for entry in cash_entries:
            amount = entry.amount
            category_sums.setdefault(entry.category, 0)
            category_sums[entry.category] += amount
            # Cash entries: negative amount means debit (outflow). We'll store amount as provided.
            tx = Transaction.create(
                date=entry.date,
                description=entry.description,
                amount=amount,
                bank='CASH',
                category=entry.category,
                merchant=None,
            )
            # Force category assignment consistent with summary accumulation
            tx.category = entry.category
            txs.append(tx)
        if txs:
            transactions_by_bank['CASH'] = txs

    def _select_strategy(self, mode: CategorizationMode) -> CategorizationStrategy:
        if mode == CategorizationMode.PROMPT_USER:
            return UserPromptStrategy(self.interaction_port, CATEGORIES)
        # AUTO and AI currently both no-op (pure processing already done)
        return AutoStrategy()

    async def _process_bank_transactions(self, year: str, month: int, mode: CategorizationMode):
        """Process transactions and delegate pending resolution to chosen strategy."""
        print(f"\n💳 Processing bank statements...")
        category_sums = {category: 0 for category in CATEGORIES}
        transactions_by_bank: Dict[str, List[Transaction]] = {}

        # Ensure CAT_MAPPING lower-case canonicalization present
        for item in CATEGORIES:
            CAT_MAPPING[item.lower()] = item.title()

        strategy_impl = self._select_strategy(mode)

        for bank_name in BANK_ACCOUNTS:
            try:
                print(f"\nProcessing {bank_name}...")
                # 1. Read raw transactions (domain objects)
                transactions = self.statement_reader.read(bank_name, year, month)

                # 2. Pure processing (no prompts)
                transactions, mapping, pending = self.transaction_processor.categorize_transactions(
                    bank_name, transactions
                )
                # mapping may be same object; assign for clarity
                self.transaction_processor.merchant_category_dict = mapping

                # 3. Resolve pending categorization via strategy if any
                if pending:
                    decisions = await strategy_impl.categorize(pending)  # type: ignore[arg-type]
                    self._apply_categorization_decisions(pending, decisions)

                # 4. Accumulate category sums & store transactions
                for tx in transactions:
                    if tx.category and tx.amount is not None:
                        category_sums[tx.category] += tx.amount
                transactions_by_bank[bank_name] = transactions
                print(f"✅ Processed {len(transactions)} transactions from {bank_name} (Pending resolved: {len(pending)})")
            except FileNotFoundError as e:
                print(f"⚠️  Skipping {bank_name}: {e}")
                continue
            except Exception as e:
                print(f"❌ Error processing {bank_name}: {e}")
                continue
        return category_sums, transactions_by_bank
    
    def _update_summary(self, year: str, month: int, category_sums: Dict[str, int]):
        """Thin wrapper delegating to SummaryService returning domain SummaryData."""
        return self.summary_service.update_summary(year, month, category_sums)
    
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
    
    async def run_async(self) -> None:
        """Async execution path (single event loop)."""
        try:
            self.setup()
            ctx = await self._get_initial_context()
            month = ctx.month
            year = str(ctx.year)
            mode = ctx.mode
            print(f"\n📊 Processing data for {calendar.month_name[month]} {year} (mode={mode.value})")

            self._download_finance_file()
            self.transaction_processor.manage_merchant_category_file(self.config.bank_folder_id)
            category_sums, transactions_by_bank = await self._process_bank_transactions(year, month, mode)

            cash_entries = await self.interaction_port.request_cash_entries(month, int(year), CATEGORIES)
            self._integrate_cash_entries(cash_entries, category_sums, transactions_by_bank)

            if self.transaction_processor.merchant_store.dirty:
                self.transaction_processor.save_merchant_category_file(self.config.bank_folder_id)

            summary_data = self._update_summary(year, month, category_sums)

            # Build and show summary view (presentation concern separated)
            summary_view = build_summary_view(month, int(year), category_sums)
            await self.interaction_port.show_summary(summary_view)

            print(f"💾 Saving results to Excel...")
            # Writer still expects DataFrame until refactor; pass domain object for future change
            self.writer.write(year, month, transactions_by_bank, summary_data, LOCAL_OUTPUT_FILE)
            self._upload_results()
            print(f"\n✅ Processing complete! Summary for {calendar.month_name[month]} {year} has been updated.")
            print(f"📊 Processed {sum(len(v) for v in transactions_by_bank.values())} total transactions")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise
        finally:
            self._cleanup()

    def run(self) -> None:
        """Public synchronous entrypoint that wraps async flow."""
        asyncio.run(self.run_async())
