"""
Draws a graph of the dependencies between modules
"""
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Iterator, Optional

from dep_check.dependency_finder import find_dependencies
from dep_check.models import GlobalDependencies, Module, SourceFile

from .app_configuration import AppConfigurationSingleton


class IGraphDrawer(ABC):
    """
    Interface for writing a dependency graph.
    """

    @abstractmethod
    def write(self, global_dep: GlobalDependencies) -> bool:
        """
        Writes a dot file corresponding to the dependency graph.
        """


def _fold_dep(
    gloabl_dep: GlobalDependencies, fold_module: Module
) -> GlobalDependencies:

    flod_global_dep = defaultdict(set)
    for module, rules in gloabl_dep.items():
        new_rules = set()
        if module.startswith(fold_module):
            module = fold_module
        fold_rule = set(
            fold_module if rule.startswith(fold_module) else rule for rule in rules
        )
        new_rules |= fold_rule
        flod_global_dep[module] |= new_rules

    return flod_global_dep


class DrawGraphUC:
    def __init__(
        self,
        drawer: IGraphDrawer,
        source_files: Iterator[SourceFile],
        config: Optional[Dict] = None,
    ):
        app_configuration = AppConfigurationSingleton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.source_files = source_files
        self.drawer = drawer
        self.config = config or {}

    def run(self) -> None:
        global_dependencies: GlobalDependencies = {}
        for source_file in self.source_files:
            dependencies = find_dependencies(source_file)
            dependencies = self.std_lib_filter.filter(dependencies)
            global_dependencies[source_file.module] = dependencies

        for fold_module in self.config.get("fold_modules", []):
            global_dependencies = _fold_dep(global_dependencies, fold_module)

        self.drawer.write(global_dependencies)
