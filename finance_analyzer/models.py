"""Domain data models (initial scaffolding for upcoming refactor).

These are currently **not** fully integrated. They will gradually replace
raw DataFrame row usage as we move toward a cleaner hexagonal core.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class Transaction:
    id: str
    date: str
    description: str
    amount: float
    bank: str
    debit: float | None = None
    credit: float | None = None
    category: Optional[str] = None
    merchant: Optional[str] = None

    def __post_init__(self) -> None:
        """Infer debit / credit if not explicitly provided.

        Convention:
          * Positive amount => credit (money in)
          * Negative amount => debit (money out) stored as positive magnitude in debit field
        If both debit and credit are already set (unlikely) we do not override.
        """
        # Don't override if both explicitly given
        if self.debit is not None or self.credit is not None:
            return

        if self.amount > 0:
            self.credit = self.amount
            self.debit = None
        elif self.amount < 0:
            self.debit = abs(self.amount)
            self.credit = None
        else:  # amount == 0
            self.debit = None
            self.credit = 0.0

    @staticmethod
    def create(
        date: str,
        description: str,
        amount: float,
        bank: str,
        debit: float | None = None,
        credit: float | None = None,
        category: str | None = None,
        merchant: str | None = None,
    ) -> "Transaction":
        return Transaction(
            id=str(uuid.uuid4()),
            date=date,
            description=description,
            amount=amount,
            bank=bank,
            debit=debit,
            credit=credit,
            category=category,
            merchant=merchant,
        )


@dataclass
class CategorizationRequest:
    transaction_id: str
    transaction: Transaction
    suggested_categories: List[str] = field(default_factory=list)


@dataclass
class CategorizationResponse:
    transaction_id: str
    selected_category: str
    save_merchant_mapping: bool = False


@dataclass
class ProcessingResult:
    processed_transactions: List[Transaction]
    category_totals: Dict[str, float]
    summary_report: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

