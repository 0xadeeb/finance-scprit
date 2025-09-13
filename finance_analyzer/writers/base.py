"""Writer abstraction decoupled from pandas.

Writers now accept:
  * transactions_by_bank: Dict[str, List[Transaction]]
  * summary: SummaryData domain object

Infrastructure writers (like Excel) may internally convert these to pandas
DataFrames for convenience/formatting, but the public interface exposed to
the core domain stays free of DataFrame coupling.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from ..models import Transaction
from ..services.summary.models import SummaryData


class Writer(ABC):
    """Abstract base class for output writers"""

    @abstractmethod
    def write(
        self,
        year: str,
        month: int,
        transactions_by_bank: Dict[str, List[Transaction]],
        summary: SummaryData,
        output_path: str,
    ) -> bool:
        """Persist financial data.

        Parameters
        ----------
        year : str
            Year of processing (sheet name for Excel).
        month : int
            Month number 1-12.
        transactions_by_bank : Dict[str, List[Transaction]]
            Domain transactions grouped by bank name.
        summary : SummaryData
            Domain summary object.
        output_path : str
            Target file path.
        """
        raise NotImplementedError

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this writer"""
        raise NotImplementedError

    @abstractmethod
    def get_writer_name(self) -> str:
        """Get the name of this writer"""
        raise NotImplementedError

    @abstractmethod
    def supports_formatting(self) -> bool:
        """Check if this writer supports advanced formatting"""
        raise NotImplementedError
