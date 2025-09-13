"""Strategy package for categorization resolution.

Exports:
- CategorizationStrategy (abstract base)
- UserPromptStrategy (current concrete implementation)
- PromptCallback (type alias for interaction callback)

Future:
- RuleBasedStrategy
- MLInferenceStrategy
- BatchAutoCategorizationStrategy
"""
from .base import CategorizationStrategy, CategorizationMode
from .user_prompt import UserPromptStrategy
from .auto import AutoStrategy

__all__ = [
    'CategorizationStrategy',
    'UserPromptStrategy',
    'CategorizationMode',
    'AutoStrategy'
]
