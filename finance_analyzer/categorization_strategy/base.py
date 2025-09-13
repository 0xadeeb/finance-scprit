"""Async strategy abstractions for categorization resolution."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, List
from enum import Enum

from ..transaction_processor import CategorizationRequest
from ..interaction.port import CategorizationDecision


class CategorizationMode(Enum):
    PROMPT_USER = "prompt_user"
    AUTO = "auto"    # pure processing only
    AI = "ai"         # placeholder for future ML/AI categorization

class CategorizationStrategy(ABC):
    """Async categorization strategy returning user (or system) decisions.

    Each decision corresponds to an index into the pending list.
    Implementations may choose to skip some (leaving them unresolved).
    """

    @abstractmethod
    async def categorize(self, pending: Iterable[CategorizationRequest]) -> List[CategorizationDecision]:
        raise NotImplementedError
