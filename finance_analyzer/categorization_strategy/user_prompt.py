"""UserPromptStrategy async implementation leveraging interaction port."""
from __future__ import annotations
from typing import Iterable, List, Sequence

from ..transaction_processor import CategorizationRequest
from ..interaction.port import AsyncInteractionPort, CategorizationItem
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..interaction.port import CategorizationDecision
from .base import CategorizationStrategy
from ..constants import CATEGORIES


class UserPromptStrategy(CategorizationStrategy):
    def __init__(self, interaction: AsyncInteractionPort, categories: Sequence[str] | None = None):
        self.interaction = interaction
        self.categories = list(categories) if categories else list(CATEGORIES)

    async def categorize(self, pending: Iterable[CategorizationRequest]) -> List[CategorizationDecision]:  # type: ignore[override]
        pending_list = list(pending)
        if not pending_list:
            return []
        items = [
            CategorizationItem(
                idx=i,
                description=req.transaction.description,
                amount=req.transaction.amount,
                merchant=req.transaction.merchant,
                date=str(req.transaction.date) if req.transaction.date else None
            ) for i, req in enumerate(pending_list)
        ]
        decisions = await self.interaction.request_categorization(items, self.categories)
        return decisions
