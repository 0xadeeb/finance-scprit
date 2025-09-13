"""Domain summary models decoupled from pandas DataFrame usage.

SummaryData represents the yearly summary sheet logically.
Each SummaryRow contains per-month values plus precomputed avg & total.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import calendar

MONTH_NAMES: List[str] = [calendar.month_name[i] for i in range(1, 13)]

@dataclass
class SummaryRow:
    name: str
    month_values: Dict[str, float]  # month name -> value
    avg: float = 0.0
    total: float = 0.0

    def recompute(self) -> None:
        values = [self.month_values.get(m, 0.0) for m in MONTH_NAMES]
        if values:
            self.avg = round(sum(values) / len(values), 2)
            self.total = round(sum(values) - self.avg, 2)
        else:
            self.avg = 0.0
            self.total = 0.0

@dataclass
class SummaryData:
    year: str
    rows: List[SummaryRow] = field(default_factory=list)

    def row_by_name(self, name: str) -> SummaryRow | None:
        for r in self.rows:
            if r.name == name:
                return r
        return None

    def ensure_row(self, name: str) -> SummaryRow:
        row = self.row_by_name(name)
        if row is None:
            row = SummaryRow(name=name, month_values={})
            self.rows.append(row)
        return row

    def recompute_all(self) -> None:
        for r in self.rows:
            r.recompute()

    def as_dict(self) -> Dict[str, Dict[str, float]]:
        return {
            r.name: {**r.month_values, 'Avg': r.avg, 'Total': r.total}
            for r in self.rows
        }
