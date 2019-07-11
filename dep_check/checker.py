"""
Check that dependencies follow a set of rules.
"""
import re
from typing import List, Optional

from dep_check.models import Module, ModuleWildcard, Rule, Rules, wildcard_to_regex


class NotAllowedDependencyException(Exception):
    """
    Exception that represents an unauthorized import in a module.
    """

    def __init__(
        self, dependency: Module, authorized_modules: List[ModuleWildcard]
    ) -> None:
        super().__init__(
            "try to import {} but only allowed to import {}".format(
                dependency, authorized_modules
            )
        )
        self.dependency = dependency
        self.authorized_modules = authorized_modules


def check_dependency(dependency: Module, rules: Rules) -> Rule:
    """
    Check that dependencies match a given set of rules.
    """
    used_rule: Optional[Rule] = None
    for module, rule in rules:
        if re.match("{}$".format(wildcard_to_regex(rule)), dependency):
            used_rule = (module, rule)
            break
    if not used_rule:
        raise NotAllowedDependencyException(dependency, [r for _, r in rules])
    return used_rule
