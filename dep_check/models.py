"""
Define all the business models of the application.
"""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterator, List, NewType, Tuple

from ordered_set import OrderedSet

Module = NewType("Module", str)


@dataclass(frozen=True)
class Dependency:
    """
    A complete information about a dependency

    With 'from a import b, c', main_import = 'a' and sub_imports = {b, c}
    With 'import e', main_import = 'e' and sub_imports = {}
    """

    main_import: Module = Module("")
    sub_imports: FrozenSet[Module] = field(default_factory=frozenset)


Dependencies = OrderedSet[Dependency]

SourceCode = NewType("SourceCode", str)

ModuleWildcard = NewType("ModuleWildcard", str)

Rule = Tuple[ModuleWildcard, ModuleWildcard]
Rules = OrderedSet[Rule]

DependencyRules = Dict[str, List[ModuleWildcard]]

GlobalDependencies = Dict[Module, Dependencies]


@dataclass(frozen=True)
class MatchingRule:
    module_wildcard: ModuleWildcard
    original_rule_wildcard: ModuleWildcard
    specific_rule_wildcard: ModuleWildcard

    @property
    def original_rule(self) -> Rule:
        return (self.module_wildcard, self.original_rule_wildcard)


MatchingRules = OrderedSet[MatchingRule]


def get_parent(module: Module) -> Module:
    """
    Get the parent module of a given one.
    """
    return Module(module.rpartition(".")[0])


def iter_all_modules(global_dep: GlobalDependencies) -> Iterator[Module]:
    def iter_(global_dep: GlobalDependencies) -> Iterator[Module]:
        for module, dependencies in global_dep.items():
            yield module
            yield from (d.main_import for d in dependencies)

    return iter(OrderedSet(iter_(global_dep)))


@dataclass
class SourceFile:
    """
    A complete information about a source file.
    """

    module: Module
    code: SourceCode


@dataclass(frozen=True)
class RegexRule:
    regex: str
    raise_if_found: bool = False
