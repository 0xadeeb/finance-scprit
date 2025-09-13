"""Factory for statement readers based on config."""
from __future__ import annotations

from typing import Optional

from .excel_reader import ExcelStatementReader
from .base import StatementReader
from ..config_manager import ConfigManager
from ..file_access import FileAccessor


class StatementReaderFactory:
    @staticmethod
    def create(config: ConfigManager, file_accessor: FileAccessor, temp_file_tracker=None) -> StatementReader:
        fmt = config.get("statement_format", "excel").lower()
        bank_folder_id = config.bank_folder_id
        if fmt == 'excel':
            return ExcelStatementReader(file_accessor, bank_folder_id, temp_file_tracker)
        raise ValueError(f"Unsupported statement_format: {fmt}")
