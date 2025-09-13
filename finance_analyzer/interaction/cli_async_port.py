"""CLI implementation of AsyncInteractionPort.
Uses background threads (asyncio.to_thread) to collect input then resolves Futures.
"""
from __future__ import annotations
import asyncio
from typing import Sequence, List
from .port import (
    AsyncInteractionPort, MonthYearSelection,
    CategorizationItem, CategorizationDecision, CashEntry,
    SummaryView
)

class CliAsyncInteractionPort(AsyncInteractionPort):
    def __init__(self):
        self._loop = asyncio.get_event_loop_policy().get_event_loop()

    # Helpers -------------------------------------------------
    def _create_future(self):
        loop = asyncio.get_running_loop()
        return loop.create_future()

    def request_initial_context(self, default_year: int = 2024):  # type: ignore[override]
        fut = self._create_future()
        async def runner():
            def ask():
                from ..categorization_strategy import CategorizationMode  # local import to avoid circular dependency
                while True:
                    try:
                        month_raw = input("\n📅 Enter the month (1-12): ").strip()
                        month = int(month_raw)
                        if not 1 <= month <= 12:
                            print("Month must be 1-12"); continue
                        break
                    except ValueError:
                        print("Enter a number for month")
                year_raw = input(f"📅 Enter the year (default {default_year}): ").strip() or str(default_year)
                try:
                    year = int(year_raw)
                except ValueError:
                    print("Invalid year, using default.")
                    year = default_year
                print("Select categorization mode:")
                modes = list(CategorizationMode)
                for i, m in enumerate(modes, 1):
                    print(f" {i}. {m.value}")
                while True:
                    mode_raw = input("Mode number: ").strip()
                    if not mode_raw.isdigit():
                        print("Enter a number"); continue
                    idx = int(mode_raw) - 1
                    if 0 <= idx < len(modes):
                        mode = modes[idx]
                        break
                    print("Out of range")
                return MonthYearSelection(month=month, year=year, mode=mode)
            try:
                result = await asyncio.to_thread(ask)
                fut.set_result(result)
            except KeyboardInterrupt:
                fut.set_exception(KeyboardInterrupt())
        asyncio.create_task(runner())
        return fut

    def request_categorization(self, items: Sequence[CategorizationItem], categories: Sequence[str], title: str = "Categorize Transactions"):  # type: ignore[override]
        fut = self._create_future()
        async def runner():
            def run_loop():
                print(f"\n=== {title} ===")
                num_cat = len(categories)
                def show_categories():
                    for i in range(0, num_cat, 4):
                        row = []
                        for j in range(i, min(i+4, num_cat)):
                            row.append(f"{j+1}. {categories[j]}")
                        print("{:<25} {:<25} {:<25} {:<25}".format(*row, *( [""]*(4-len(row)) )))
                decisions: List[CategorizationDecision] = []
                for item in items:
                    print(f"\nItem {item.idx + 1} of {len(items)}: {item.description}")
                    if item.amount is not None:
                        print(f"Amount: {item.amount}")
                    if item.merchant:
                        print(f"Merchant: {item.merchant}")
                    show_categories()
                    # Category selection
                    while True:
                        raw = input("Select category number: ").strip()
                        if not raw.isdigit():
                            print("Enter a number"); continue
                        cat_idx = int(raw) - 1
                        if 0 <= cat_idx < num_cat:
                            category = categories[cat_idx]
                            break
                        print("Out of range")
                    # Remember mapping
                    remember_raw = input("Remember merchant mapping? (y/[n]): ").strip().lower()
                    remember = True if remember_raw == 'y' else False
                    decisions.append(CategorizationDecision(idx=item.idx, category=category, remember_mapping=remember))
                return decisions
            try:
                result = await asyncio.to_thread(run_loop)
                fut.set_result(result)
            except KeyboardInterrupt:
                fut.set_exception(KeyboardInterrupt())
        asyncio.create_task(runner())
        return fut

    def request_cash_entries(self, month: int, year: int, categories: Sequence[str]):  # type: ignore[override]
        fut = self._create_future()
        async def runner():
            def run_loop():
                entries: List[CashEntry] = []
                print(f"\n🧾 Add Cash Transactions for {month}/{year}")
                print("Leave blank when prompted for 'Add another' to finish.")
                num_cat = len(categories)
                def show_categories():
                    for i in range(0, num_cat, 4):
                        row = []
                        for j in range(i, min(i+4, num_cat)):
                            row.append(f"{j+1}. {categories[j]}")
                        print("{:<25} {:<25} {:<25} {:<25}".format(*row, *( [""]*(4-len(row)) )))
                while True:
                    cont = input("Add cash entry? (y/[n]): ").strip().lower()
                    if cont not in ('y', 'yes'):
                        break
                    date = input(" Date (YYYY-MM-DD) [default first day]: ").strip() or f"{year}-{month:02d}-01"
                    desc = input(" Description: ").strip() or "Cash Expense"
                    while True:
                        amt_raw = input(" Amount: ").strip()
                        try:
                            amount = float(amt_raw)
                            break
                        except ValueError:
                            print("  Invalid number")
                    # category selection
                    show_categories()
                    while True:
                        raw = input(" Select category number: ").strip()
                        if raw.isdigit():
                            cidx = int(raw) - 1
                            if 0 <= cidx < num_cat:
                                cat = categories[cidx]
                                break
                        print("  Invalid selection")
                    entries.append(CashEntry(date=date, description=desc, amount=amount, category=cat))
                return entries
            try:
                result = await asyncio.to_thread(run_loop)
                fut.set_result(result)
            except KeyboardInterrupt:
                fut.set_exception(KeyboardInterrupt())
        asyncio.create_task(runner())
        return fut

    def show_summary(self, summary: SummaryView):  # type: ignore[override]
        fut = self._create_future()
        async def runner():
            def render():
                print("\n===== SUMMARY =====")
                print(f"Period: {summary.month}/{summary.year}")
                for line in summary.categories:
                    print(f" {line.category:<25} {line.total:>12.2f}")
                print("------------------------------")
                print(f" Income:       {summary.total_income:>12.2f}")
                print(f" Expense:      {summary.total_expense:>12.2f}")
                print(f" Net:          {summary.net:>12.2f}")
                input("\nPress Enter to continue...")
            try:
                await asyncio.to_thread(render)
                fut.set_result(None)
            except KeyboardInterrupt:
                fut.set_exception(KeyboardInterrupt())
        asyncio.create_task(runner())
        return fut

    def notify(self, message: str, level: str = "info") -> None:  # type: ignore[override]
        icons = {"info": "ℹ️", "warn": "⚠️", "error": "❌", "success": "✅"}
        icon = icons.get(level, "ℹ️")
        print(f"{icon} {message}")
