"""
Bank registry for easy access to all bank parsers.
"""

from typing import Dict, Optional
from .base import Bank
from .sbi import SBIBank
from .hdfc import HDFCBank


# Bank registry for easy access
BANK_REGISTRY: Dict[str, Bank] = {
    'sbi': SBIBank(),
    'hdfc': HDFCBank()
}


class BankParserRegistry:
    """Registry for bank parsers"""
    
    @staticmethod
    def get_bank(bank_name: str) -> Optional[Bank]:
        """Get bank parser by name"""
        return BANK_REGISTRY.get(bank_name.lower())
    
    @staticmethod
    def list_banks() -> list:
        """List all available bank parsers"""
        return list(BANK_REGISTRY.keys())
    
    @staticmethod
    def register_bank(name: str, bank_parser: Bank) -> None:
        """Register a new bank parser"""
        BANK_REGISTRY[name.lower()] = bank_parser
