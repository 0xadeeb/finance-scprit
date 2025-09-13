"""SummaryService extracts the summary update logic from FinanceAnalyzer.

This is a direct refactor of the previous _update_summary method to
facilitate future orchestration refactoring. No business logic changes.
"""
from __future__ import annotations

import calendar
from typing import Dict
import pandas as pd

from ..constants import (
    LOCAL_OUTPUT_FILE,
    CREDIT_CATEGORIES,
    DEBIT_CATEGORIES,
    NET_CATEGORIES,
    BALANCE_ROWS,
)


class SummaryService:
    """Encapsulates logic for updating the yearly summary worksheet."""

    def update_summary(self, year: str, month: int, category_sums: Dict[str, int]) -> pd.DataFrame:
        """Load, mutate, and return the updated summary DataFrame.

        Parameters
        ----------
        year : str
            Year sheet name in the Excel workbook.
        month : int
            Month number (1-12).
        category_sums : Dict[str, int]
            Aggregated category totals for the month.
        """
        print(f"\n📈 Generating summary...")

        # Load existing summary
        with pd.ExcelFile(LOCAL_OUTPUT_FILE, engine="openpyxl") as xls:
            summary_df = pd.read_excel(xls, year, index_col=0)

        # Update summary with new data
        month_name = calendar.month_name[month]
        for category, total in category_sums.items():
            summary_df.loc[category, month_name] = total

        monthly_columns = [calendar.month_name[i + 1] for i in range(12)]

        # Calculate totals
        summary_df.loc["Total Credit", month_name] = sum(
            summary_df.loc[category, month_name] for category in CREDIT_CATEGORIES
        )
        summary_df.loc["Total Debit", month_name] = sum(
            summary_df.loc[category, month_name] for category in DEBIT_CATEGORIES
        )
        summary_df.loc["Total NET", month_name] = sum(
            summary_df.loc[category, month_name] for category in NET_CATEGORIES
        )

        # Calculate averages and totals
        summary_df["Avg"] = summary_df[monthly_columns].mean(axis=1).round(2)
        summary_df["Total"] = summary_df[monthly_columns].sum(axis=1).round(2) - summary_df["Avg"]

        # Update balances
        summary_df.loc["Closing Bank Bal.", month_name] = (
            summary_df.loc["Opening Bank Bal.", month_name]
            + summary_df.loc["Total Credit", month_name]
            + summary_df.loc["Total Debit", month_name]
        )
        summary_df.loc["Closing In Hand", month_name] = (
            summary_df.loc["Opening In Hand", month_name]
        )

        # Update next month opening (except December)
        if month != 12:
            next_month = calendar.month_name[month + 1]
            summary_df.loc["Opening Bank Bal.", next_month] = summary_df.loc[
                "Closing Bank Bal.", month_name
            ]
            summary_df.loc["Opening In Hand", next_month] = summary_df.loc[
                "Closing In Hand", month_name
            ]

        # Reorder rows
        ordered_rows = (
            BALANCE_ROWS[:2]
            + CREDIT_CATEGORIES
            + ["Total Credit"]
            + DEBIT_CATEGORIES
            + ["Total Debit"]
            + NET_CATEGORIES
            + ["Total NET"]
            + BALANCE_ROWS[2:]
        )

        if len(summary_df) != len(ordered_rows):
            print("❌ Summary DataFrame structure mismatch")
            print(f"Expected rows: {len(ordered_rows)}")
            print(f"Actual rows: {len(summary_df)}")
            print(f"Actual index: {summary_df.index.values}")
            raise Exception("Summary DataFrame structure mismatch")

        summary_df = summary_df.reindex(ordered_rows)
        return summary_df
