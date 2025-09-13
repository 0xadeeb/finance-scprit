"""Interaction abstractions for user-driven flows (CLI/GUI/Android extensible).

All methods return asyncio.Future objects so the caller decides when to await.
Current implementation focus: CLI; architecture supports future GUI without rewrite.
"""
from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Sequence, TYPE_CHECKING
if TYPE_CHECKING:  # avoid runtime cycle
    from ..categorization_strategy import CategorizationMode

@dataclass
class MonthYearSelection:
    month: int
    year: int
    mode: CategorizationMode

@dataclass
class CategorizationItem:
    idx: int
    description: str
    amount: float | None
    merchant: str | None
    date: str | None = None
    suggested_category: str | None = None

@dataclass
class CategorizationDecision:
    idx: int
    category: str
    remember_mapping: bool

@dataclass
class CashEntry:
    date: str
    description: str
    amount: float
    category: str

@dataclass
class SummaryCategoryLine:
    category: str
    total: float

@dataclass
class SummaryView:
    month: int
    year: int
    categories: List[SummaryCategoryLine]
    total_income: float
    total_expense: float
    net: float

class AsyncInteractionPort(ABC):
    """Abstract async interaction port. Implementations fulfill Futures."""

    # --- Initial Context ---
    @abstractmethod
    def request_initial_context(self, default_year: int = 2024) -> asyncio.Future[MonthYearSelection]:
        ...

    # --- Categorization ---
    @abstractmethod
    def request_categorization(
        self,
        items: Sequence[CategorizationItem],
        categories: Sequence[str],
        title: str = "Categorize Transactions"
    ) -> asyncio.Future[List[CategorizationDecision]]:
        ...

    # --- Cash Entries ---
    @abstractmethod
    def request_cash_entries(
        self,
        month: int,
        year: int,
        categories: Sequence[str]
    ) -> asyncio.Future[List[CashEntry]]:
        ...

    # --- Summary Display (non-blocking or simple ack) ---
    @abstractmethod
    def show_summary(self, summary: SummaryView) -> asyncio.Future[None]:
        ...

    # --- Notifications ---
    def notify(self, message: str, level: str = "info") -> None:
        pass
