"""
Define all the business models of the application.
"""

from dataclasses import dataclass
from typing import Dict, List, NewType, Set

Module = NewType("Module", str)
Dependencies = Set[Module]
SourceCode = NewType("SourceCode", str)

Rule = NewType("Rule", str)
Rules = List[Rule]

DependencyRules = Dict[str, Rules]


def get_parent(module: Module) -> Module:
    """
    Get the parent module of a given one.
    """
    return Module(module.rpartition(".")[0])


def build_rule(module: Module) -> Rule:
    """
    Return a rule that accept the given Module
    """
    module_regex = module.replace(".", "\\.").replace("*", ".*")
    module_regex = module_regex.replace("[!", "[^").replace("?", ".?")
    return Rule(module_regex)


def build_module_regex(module: Module) -> str:
    """
    Return a regex expression for the Module from wildcard
    """
    module_regex = module.replace(".", "\\.").replace("*", ".*")
    module_regex = module_regex.replace("[!", "[^").replace("?", ".?")
    return module_regex


@dataclass
class SourceFile:
    """
    A complete information about a source file.
    """

    module: Module
    code: SourceCode
