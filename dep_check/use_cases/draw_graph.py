"""
Draws a graph of the dependencies between modules
"""
from abc import ABC, abstractmethod
from typing import Dict, Iterator

from dep_check.dependency_finder import find_dependencies
from dep_check.models import Dependencies, DependencyRules, Module, Rule, SourceFile

from .app_configuration import AppConfigurationSingelton


class IGraphDrawer(ABC):
    """
    Interface for writing a dependency graph.
    """

    @abstractmethod
    def write(self, dep_rules: DependencyRules) -> bool:
        """
        Writes a dot file corresponding to the dependency graph.
        """


class DrawGraphUC:
    def __init__(self, drawer: IGraphDrawer, source_files: Iterator[SourceFile]):
        app_configuration = AppConfigurationSingelton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.source_files = source_files
        self.drawer = drawer
        self.draw_svg = True

    def run(self) -> None:
        global_dependencies: Dict[Module, Dependencies] = {}
        for source_file in self.source_files:
            dependencies = find_dependencies(source_file)
            dependencies = self.std_lib_filter.filter(dependencies)
            global_dependencies[source_file.module] = dependencies

        dependency_rules = {}
        for module, dependencies in global_dependencies.items():
            dependency_rules[module] = [Rule(dependency) for dependency in dependencies]

        self.drawer.write(dependency_rules)
