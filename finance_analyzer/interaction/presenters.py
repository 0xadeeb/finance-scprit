"""Presentation helper functions for building interaction view models.

Keeps orchestration layer (FinanceAnalyzer) lean by moving formatting and
aggregation logic that prepares view DTOs for the interaction port.
"""
from __future__ import annotations
from typing import Dict, List

from .port import SummaryView, SummaryCategoryLine


def build_summary_view(month: int, year: int, category_sums: Dict[str, float]) -> SummaryView:
    """Create a SummaryView DTO from raw category sums.

    Positive values are treated as income; negative as expenses.
    """
    lines: List[SummaryCategoryLine] = [
        SummaryCategoryLine(category=k, total=v) for k, v in category_sums.items()
    ]
    total_income = sum(v for v in category_sums.values() if v > 0)
    total_expense = sum(-v for v in category_sums.values() if v < 0)
    net = total_income - total_expense
    return SummaryView(
        month=month,
        year=year,
        categories=lines,
        total_income=total_income,
        total_expense=total_expense,
        net=net,
    )
