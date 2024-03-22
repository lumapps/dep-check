"""
Common use cases interfaces.
"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from dep_check.models import Dependencies, DependencyRules


class UnusedLevel(enum.Enum):
    IGNORE = "ignore"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Configuration:
    """
    The configuration for the tools.
    """

    dependency_rules: DependencyRules = field(default_factory=dict)
    local_init: bool = False
    unused_level: str = UnusedLevel.WARNING.value


class IStdLibFilter(ABC):
    """
    Filter for remove stdlib from dependencies.
    """

    @abstractmethod
    def filter(self, dependencies: Dependencies) -> Dependencies:
        """
        Remove dependencies that are part of stdlib.
        """
