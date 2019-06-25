"""
Common use cases interfaces.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from dep_check.models import Dependencies, DependencyRules


@dataclass
class Configuration:
    """
    The configuration for the tools.
    """

    dependency_rules: DependencyRules = field(default_factory=dict)
    local_init: bool = False


class IStdLibFilter(ABC):
    """
    Filter for remove stdlib from dependencies.
    """

    @abstractmethod
    def filter(self, dependencies: Dependencies) -> Dependencies:
        """
        Remove dependencies that are part of stdlib.
        """


class ExitCode(Enum):
    """
    Describe possible exit codes
    """

    OK = 0
    KO = 1
