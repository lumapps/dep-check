"""
Check that dependencies follow a set of rules.
"""

import re
from typing import List

from ordered_set import OrderedSet

from dep_check.dependency_finder import IParser
from dep_check.models import Dependency, MatchingRules, Module, ModuleWildcard


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


def _raise_on_forbidden_rules(
    parser: IParser, dependency: Dependency, matching_rules: MatchingRules
) -> MatchingRules:
    # pylint: disable=too-many-nested-blocks
    used_rules: MatchingRules = OrderedSet()
    imports = [
        dependency.main_import,
        *[
            Module(f"{dependency.main_import}.{sub_import}")
            for sub_import in dependency.sub_imports
        ],
    ]
    for module in imports:
        for matching_rule in matching_rules:
            regex_rule = parser.wildcard_to_regex(matching_rule.specific_rule_wildcard)
            if regex_rule.raise_if_found:
                if re.match(f"{regex_rule.regex}$", module):
                    raise NotAllowedDependencyException(
                        module, [r.specific_rule_wildcard for r in matching_rules]
                    )
                used_rules.add(matching_rule)

    return used_rules


def _find_matching_rules(
    parser: IParser, matching_rules: MatchingRules, dotted_import: Module
) -> MatchingRules:
    used_rules: MatchingRules = OrderedSet()

    for matching_rule in matching_rules:
        regex_rule = parser.wildcard_to_regex(matching_rule.specific_rule_wildcard)
        if regex_rule.raise_if_found:
            # Don't want to handle if here, it should have been done earlier in the flow
            continue
        if re.match(f"{regex_rule.regex}$", dotted_import):
            used_rules.add(matching_rule)

    return used_rules


def check_dependency(
    parser: IParser, dependency: Dependency, matching_rules: MatchingRules
) -> MatchingRules:
    """
    Check that dependencies match a given set of rules.
    """

    forbidden_rules = _raise_on_forbidden_rules(parser, dependency, matching_rules)
    used_rules = _find_matching_rules(parser, matching_rules, dependency.main_import)
    if used_rules:
        return OrderedSet([*used_rules, *forbidden_rules])

    if not dependency.sub_imports:
        raise NotAllowedDependencyException(
            dependency.main_import, [r.specific_rule_wildcard for r in matching_rules]
        )

    return OrderedSet(
        [
            *check_import_from_dependency(parser, dependency, matching_rules),
            *forbidden_rules,
        ]
    )


def check_import_from_dependency(
    parser: IParser, dependency: Dependency, matching_rules: MatchingRules
) -> MatchingRules:
    used_rules: MatchingRules = OrderedSet()
    for import_module in dependency.sub_imports:
        module = Module(f"{dependency.main_import}.{import_module}")
        matched_rules = _find_matching_rules(parser, matching_rules, module)
        used_rules.update(matched_rules)
        if not matched_rules:
            raise NotAllowedDependencyException(
                module, [r.specific_rule_wildcard for r in matching_rules]
            )
    return used_rules
