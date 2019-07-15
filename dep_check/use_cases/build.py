"""
Build rules more restrictive rules from existing source use case.
"""
from abc import ABC, abstractmethod
from typing import Dict, Iterator

from dep_check.dependency_finder import find_dependencies
from dep_check.models import Dependencies, Module, ModuleWildcard, SourceFile

from .app_configuration import AppConfigurationSingleton
from .interfaces import Configuration


class IConfigurationWriter(ABC):
    """
    Interface for writing a script configuration.
    """

    @abstractmethod
    def write(self, configuration: Configuration) -> None:
        """
        Write a script configuration.
        """


class BuildConfigurationUC:
    """
    Build more restrictive rules from existing list of files.
    """

    def __init__(
        self, printer: IConfigurationWriter, source_files: Iterator[SourceFile]
    ) -> None:
        app_configuration = AppConfigurationSingleton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.printer = printer
        self.source_files = source_files

    def run(self) -> None:
        """
        Build configuration from existing source files.
        """
        global_dependencies: Dict[Module, Dependencies] = {}
        for source_file in self.source_files:
            dependencies = find_dependencies(source_file)
            dependencies = self.std_lib_filter.filter(dependencies)

            global_dependencies[source_file.module] = dependencies

        dependency_rules = {}
        for module, dependencies in global_dependencies.items():
            dependency_rules[str(module)] = [
                ModuleWildcard(dependency.main_import) for dependency in dependencies
            ]

        self.printer.write(Configuration(dependency_rules))
