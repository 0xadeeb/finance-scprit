"""Abstract base for statement readers producing domain Transactions.

Readers hide file format (excel, json, csv, api) and emit a list of
`Transaction` objects for the requested bank+year+month.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import Transaction


class StatementReader(ABC):
    """Abstract base class for reading bank statements into domain transactions."""

    @abstractmethod
    def read(self, bank_name: str, year: str, month: int) -> List[Transaction]:  # pragma: no cover - interface
        """Return list of transactions for given bank & period."""
        raise NotImplementedError

    @abstractmethod
    def get_format(self) -> str:  # pragma: no cover - interface
        """Return the underlying statement format (e.g. 'excel', 'json')."""
        raise NotImplementedError
