"""SummaryService extracts the summary update logic from FinanceAnalyzer.

This is a direct refactor of the previous _update_summary method to
facilitate future orchestration refactoring. No business logic changes.
"""
from __future__ import annotations

import calendar
from typing import Dict
import pandas as pd

from ...constants import (
    LOCAL_OUTPUT_FILE,
    CREDIT_CATEGORIES,
    DEBIT_CATEGORIES,
    NET_CATEGORIES,
    BALANCE_ROWS,
)
from .models import SummaryData, SummaryRow


class SummaryService:
    """Encapsulates logic for updating the yearly summary worksheet."""

    def update_summary(self, year: str, month: int, category_sums: Dict[str, int]) -> SummaryData:
        """Load, mutate, and return the updated SummaryData domain object.

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

        # Load existing summary (pandas internal)
        with pd.ExcelFile(LOCAL_OUTPUT_FILE, engine="openpyxl") as xls:
            df = pd.read_excel(xls, year, index_col=0)

        # Update summary with new data
        month_name = calendar.month_name[month]
        for category, total in category_sums.items():
            if category in df.index:
                df.loc[category, month_name] = total

        monthly_columns = [calendar.month_name[i + 1] for i in range(12)]

        # Calculate totals
        df.loc["Total Credit", month_name] = sum(
            df.loc[category, month_name] for category in CREDIT_CATEGORIES
        )
        df.loc["Total Debit", month_name] = sum(
            df.loc[category, month_name] for category in DEBIT_CATEGORIES
        )
        df.loc["Total NET", month_name] = sum(
            df.loc[category, month_name] for category in NET_CATEGORIES
        )

        # Calculate averages and totals
        df["Avg"] = df[monthly_columns].mean(axis=1).round(2)
        df["Total"] = df[monthly_columns].sum(axis=1).round(2) - df["Avg"]

        # Update balances
        df.loc["Closing Bank Bal.", month_name] = (
            df.loc["Opening Bank Bal.", month_name]
            + df.loc["Total Credit", month_name]
            + df.loc["Total Debit", month_name]
        )
        df.loc["Closing In Hand", month_name] = (
            df.loc["Opening In Hand", month_name]
        )

        # Update next month opening (except December)
        if month != 12:
            next_month = calendar.month_name[month + 1]
            df.loc["Opening Bank Bal.", next_month] = df.loc[
                "Closing Bank Bal.", month_name
            ]
            df.loc["Opening In Hand", next_month] = df.loc[
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

        if len(df) != len(ordered_rows):
            print("❌ Summary DataFrame structure mismatch")
            print(f"Expected rows: {len(ordered_rows)}")
            print(f"Actual rows: {len(df)}")
            print(f"Actual index: {df.index.values}")
            raise Exception("Summary DataFrame structure mismatch")
        df = df.reindex(ordered_rows)

        # Build SummaryData
        summary = SummaryData(year=year)
        for row_name in ordered_rows:
            month_values = {m: float(df.loc[row_name, m]) for m in monthly_columns if m in df.columns}
            avg = float(df.loc[row_name, 'Avg']) if 'Avg' in df.columns else 0.0
            total = float(df.loc[row_name, 'Total']) if 'Total' in df.columns else 0.0
            summary.rows.append(SummaryRow(name=row_name, month_values=month_values, avg=avg, total=total))
        return summary
