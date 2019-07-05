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
    global_dep: GlobalDependencies, fold_module: Module
) -> GlobalDependencies:

    fold_global_dep = defaultdict(set)
    for module, rules in global_dep.items():
        new_rules = set()
        if module.startswith(fold_module):
            module = fold_module
        fold_rule = set(
            fold_module if rule.startswith(fold_module) else rule for rule in rules
        )
        new_rules |= fold_rule
        fold_global_dep[module] |= new_rules

    return fold_global_dep


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

    def _hide(self, global_dep: GlobalDependencies) -> GlobalDependencies:
        hide_modules = tuple(self.config.get("hide_modules", ()))
        if not hide_modules:
            return global_dep

        filtered_global_dep = {}
        for module, dependencies in global_dep.items():
            if not module.startswith(hide_modules):

                filtered_global_dep[module] = set(
                    dependency
                    for dependency in dependencies
                    if not dependency.startswith(hide_modules)
                )

        return filtered_global_dep

    def run(self) -> None:
        global_dependencies: GlobalDependencies = {}
        for source_file in self.source_files:
            module = source_file.module.replace(".__init__", "")
            dependencies = find_dependencies(source_file)
            dependencies = self.std_lib_filter.filter(dependencies)
            global_dependencies[module] = dependencies

        global_dependencies = self._hide(global_dependencies)

        for fold_module in self.config.get("fold_modules", []):
            global_dependencies = _fold_dep(global_dependencies, fold_module)

        # To avoid a module to point itself, and make the graph more readable
        for module, deps in global_dependencies.items():
            deps.discard(module)

        self.drawer.write(global_dependencies)
