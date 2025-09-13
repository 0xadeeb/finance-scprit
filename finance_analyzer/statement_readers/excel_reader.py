"""Excel implementation of StatementReader using existing bank parser registry."""
from __future__ import annotations

import os
import calendar
import pandas as pd
from typing import List

from .base import StatementReader
from ..bank_parsers import BankParserRegistry
from ..file_access import FileAccessor
from ..constants import TEMP_DIR
from ..models import Transaction


class ExcelStatementReader(StatementReader):
    def __init__(self, file_accessor: FileAccessor, bank_folder_base: str, temp_file_tracker=None):
        self.file_accessor = file_accessor
        self.bank_folder_base = bank_folder_base
        self.temp_file_tracker = temp_file_tracker

    def get_format(self) -> str:
        return "excel"

    def _resolve_statement_path(self, bank_name: str, year: str, month: int) -> str:
        filename = f"Bankstatement{calendar.month_abbr[month]}.xlsx"
        if hasattr(self.file_accessor, 'find_file_in_folder'):
            # Cloud traversal
            bank_folder_id = self.file_accessor.find_file_in_folder(self.bank_folder_base, bank_name)
            if not bank_folder_id:
                raise FileNotFoundError(f"Bank folder '{bank_name}' not found in cloud storage")
            year_folder_id = self.file_accessor.find_file_in_folder(bank_folder_id, year)
            if not year_folder_id:
                raise FileNotFoundError(f"Year folder '{year}' not found in bank folder '{bank_name}'")
            file_id = self.file_accessor.find_file_in_folder(year_folder_id, filename)
            if not file_id:
                raise FileNotFoundError(f"File '{filename}' not found in {bank_name}/{year}")
            return file_id
        else:
            local_path = f"{self.bank_folder_base}/{bank_name}/{year}/{filename}"
            if not self.file_accessor.exists(local_path):
                raise FileNotFoundError(f"File '{local_path}' not found")
            return local_path

    def read(self, bank_name: str, year: str, month: int) -> List[Transaction]:
        file_path = self._resolve_statement_path(bank_name, year, month)
        temp_file = os.path.join(TEMP_DIR, f"{bank_name}_{year}_{month}.xlsx")
        if self.temp_file_tracker:
            self.temp_file_tracker(temp_file)
        if not self.file_accessor.download_to_temp(file_path, temp_file):
            raise Exception(f"Failed to download statement file for {bank_name} {year}-{month}")

        bank_instance = BankParserRegistry.get_bank(bank_name.lower())
        if not bank_instance:
            raise ValueError(f"Unknown bank: {bank_name}")

        # Diagnostic logging for parser configuration
        try:
            print(
                f"[Parser] Using {bank_instance.__class__.__name__} for bank={bank_name} "
                f"skiprows={getattr(bank_instance,'skiprows',None)} "
                f"date_col={getattr(bank_instance,'date_col',None)} "
                f"description_col={getattr(bank_instance,'description_col',None)} "
                f"credit_col={getattr(bank_instance,'credit_col',None)} "
                f"debit_col={getattr(bank_instance,'debit_col',None)}"
            )
        except Exception:
            pass

        name_mapping = bank_instance.get_column_mapping()
        raw_df = pd.read_excel(temp_file, skiprows=bank_instance.skiprows)
        raw_df.rename(name_mapping, axis='columns', inplace=True)

        # Standardize columns expected: Date, Description, Credit, Debit
        raw_df['Date'] = pd.to_datetime(
            raw_df['Date'], errors='coerce', dayfirst=True, format='mixed'
        )

        # Clean up: drop fully empty rows and rows where all financial columns are NaN
        df = raw_df
        # Normalize description to string early for filtering
        df['Description'] = df['Description'].astype(str).str.strip()

        transactions: List[Transaction] = []
        consecutive_blank = 0
        for _, row in df.iterrows():
            date_val = row['Date']
            desc = row['Description']
            credit_raw = row.get('Credit')
            debit_raw = row.get('Debit')

            # Stop criteria: after we see a few consecutive blank financial rows we assume footer area
            is_credit_nan = pd.isna(credit_raw) or (isinstance(credit_raw, str) and credit_raw.strip() == '')
            is_debit_nan = pd.isna(debit_raw) or (isinstance(debit_raw, str) and debit_raw.strip() == '')

            if is_credit_nan and is_debit_nan and (pd.isna(date_val) or desc == '' or desc.lower() == 'nan'):
                consecutive_blank += 1
            else:
                consecutive_blank = 0
            if consecutive_blank >= 1:
                break

            # Skip rows with no date and no meaningful description
            if pd.isna(date_val) and (desc == '' or desc.lower() == 'nan'):
                continue

            # Skip heading/footer like rows (common patterns)
            lowered = desc.lower()
            if lowered.startswith('opening balance') or lowered.startswith('closing balance'):
                continue

            # Convert date to desired string format (if valid)
            date_str = date_val.strftime('%d %b %Y') if not pd.isna(date_val) else ''

            credit = None if is_credit_nan else float(credit_raw)
            debit = None if is_debit_nan else float(debit_raw)
            if credit is not None and debit is not None:
                # Ambiguous row; compute net
                amount = credit - debit
            elif credit is not None:
                amount = credit
            elif debit is not None:
                amount = -debit
            else:
                # No financial info; skip
                continue

            transactions.append(
                Transaction.create(
                    date=date_str,
                    description=desc,
                    amount=amount,
                    bank=bank_name.upper(),
                    debit=debit,
                    credit=credit,
                )
            )

        try:
            os.remove(temp_file)
        except Exception:
            pass
        return transactions
