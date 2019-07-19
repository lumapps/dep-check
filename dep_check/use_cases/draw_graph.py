"""
Draws a graph of the dependencies between modules
"""
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Iterator, Optional

from dep_check.dependency_finder import IParser, get_dependencies
from dep_check.models import (
    Dependencies,
    Dependency,
    GlobalDependencies,
    Module,
    SourceFile,
)

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

    fold_global_dep: GlobalDependencies = defaultdict(set)
    for module, deps in global_dep.items():
        new_deps: Dependencies = set()
        if module.startswith(tuple((f"{fold_module}.", f"{fold_module}/"))):
            module = fold_module
        fold_dep = set(
            Dependency(fold_module) if dep.main_import.startswith(fold_module) else dep
            for dep in deps
        )
        new_deps |= fold_dep
        fold_global_dep[module] |= new_deps

    return fold_global_dep


class DrawGraphUC:
    def __init__(
        self,
        drawer: IGraphDrawer,
        parser: IParser,
        source_files: Iterator[SourceFile],
        config: Optional[Dict] = None,
    ):
        app_configuration = AppConfigurationSingleton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.source_files = source_files
        self.drawer = drawer
        self.parser = parser
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
                    if not dependency.main_import.startswith(hide_modules)
                )

        return filtered_global_dep

    def run(self) -> None:
        global_dependencies: GlobalDependencies = {}
        for source_file in self.source_files:
            module = Module(source_file.module.replace(".__init__", ""))
            dependencies = get_dependencies(source_file, self.parser)
            dependencies = self.std_lib_filter.filter(dependencies)
            global_dependencies[module] = dependencies

        global_dependencies = self._hide(global_dependencies)

        for fold_module in self.config.get("fold_modules", []):
            global_dependencies = _fold_dep(global_dependencies, fold_module)

        # To avoid a module to point itself, and make the graph more readable
        for module, deps in list(global_dependencies.items()):
            deps -= {dep for dep in deps if dep.main_import == module}

            if not global_dependencies[module]:
                global_dependencies.pop(module, None)

        self.drawer.write(global_dependencies)
