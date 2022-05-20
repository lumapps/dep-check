"""
Check that dependencies follow a set of rules.
"""
import re
from typing import List, Optional

from dep_check.dependency_finder import IParser
from dep_check.models import Dependency, Module, ModuleWildcard, Rule, Rules


class NotAllowedDependencyException(Exception):
    """
    Exception that represents an unauthorized import in a module.
    """

    def __init__(
        self, dependency: Module, authorized_modules: List[ModuleWildcard]
    ) -> None:
        super().__init__(
            f"try to import {dependency} but only allowed to import {authorized_modules}"
        )
        self.dependency = dependency
        self.authorized_modules = authorized_modules


def check_dependency(parser: IParser, dependency: Dependency, rules: Rules) -> Rules:
    """
    Check that dependencies match a given set of rules.
    """
    used_rule: Optional[Rule] = None
    for module, rule in rules:
        if re.match(f"{parser.wildcard_to_regex(rule)}$", dependency.main_import):
            used_rule = (module, rule)
            return set((used_rule,))
    if not dependency.sub_imports:
        raise NotAllowedDependencyException(
            dependency.main_import, [r for _, r in rules]
        )

    return check_import_from_dependency(parser, dependency, rules)


def check_import_from_dependency(
    parser: IParser, dependency: Dependency, rules: Rules
) -> Rules:
    used_rules: Rules = set()
    for import_module in dependency.sub_imports:
        used_rule = None
        for module, rule in rules:
            if re.match(
                f"{parser.wildcard_to_regex(rule)}$",
                f"{dependency.main_import}.{import_module}",
            ):
                used_rule = (module, rule)
                used_rules.add(used_rule)
        if not used_rule:
            raise NotAllowedDependencyException(
                Module(f"{dependency.main_import}.{import_module}"),
                [r for _, r in rules],
            )
    return used_rules
