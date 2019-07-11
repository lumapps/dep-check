"""
Check that dependencies follow a set of rules.
"""
import re
from typing import List, Optional, Tuple

from dep_check.models import Module, ModuleWildcard, Rules, wildcard_to_regex


class NotAllowedDependencyException(Exception):
    """
    Exception that represents an unauthorized import in a module.
    """

    def __init__(self, dependency: Module, rules: Rules) -> None:
        super().__init__(
            "try to import {} but only allowed to import {}".format(dependency, rules)
        )
        self.dependency = dependency
        self.rules = rules


def check_dependency(
    dependency: Module, rules: List[Tuple[ModuleWildcard, ModuleWildcard]]
) -> Tuple[ModuleWildcard, ModuleWildcard]:
    """
    Check that dependencies match a given set of rules.
    """
    used_rule: Optional[Tuple[ModuleWildcard, ModuleWildcard]] = None
    for module, rule in rules:
        if re.match("{}$".format(wildcard_to_regex(rule)), dependency):
            used_rule = (module, rule)
            break
    if not used_rule:
        raise NotAllowedDependencyException(dependency, [r for _, r in rules])
    return used_rule
