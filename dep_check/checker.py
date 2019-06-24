"""
Check that dependencies follow a set of rules.
"""
import re

from models import Module, Rules


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


def check_dependency(dependency: Module, rules: Rules) -> None:
    """
    Check that dependencies match a given set of rules.
    """
    if not any(re.match("{}$".format(rule), dependency) for rule in rules):
        raise NotAllowedDependencyException(dependency, rules)
