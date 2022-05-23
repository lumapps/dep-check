"""
Common use cases interfaces.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from dep_check.models import Dependencies, DependencyRules


@dataclass
class Configuration:
    """
    The configuration for the tools.
    """

    dependency_rules: DependencyRules = field(default_factory=dict)
    lang: str = "python"
    local_init: bool = False
    error_on_unused: bool = False


class IStdLibFilter(ABC):
    """
    Filter for remove stdlib from dependencies.
    """

    @abstractmethod
    def filter(self, dependencies: Dependencies) -> Dependencies:
        """
        Remove dependencies that are part of stdlib.
        """
