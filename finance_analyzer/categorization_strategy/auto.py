from .base import CategorizationStrategy
from typing import Iterable, List
from ..transaction_processor import CategorizationRequest
from ..interaction.port import CategorizationDecision

class AutoStrategy(CategorizationStrategy):
    """Returns no decisions (AUTO/AI placeholder)."""
    async def categorize(self, pending: Iterable[CategorizationRequest]) -> List[CategorizationDecision]:  # type: ignore[override]
        return list(
            map(
                lambda t: CategorizationDecision(idx=t[0], category='Misl', remember_mapping=False),
                enumerate(pending)
           )
        )