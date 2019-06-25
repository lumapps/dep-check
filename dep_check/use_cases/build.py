"""
Build rules more restrictive rules from exsiting source use case.
"""
from abc import ABC, abstractmethod
from typing import Dict, Iterator

from dep_check.dependency_finder import find_dependencies
from dep_check.models import (
    Dependencies,
    Module,
    SourceFile,
    build_module_regex,
    build_rule,
)

from .app_configuration import AppConfigurationSingelton
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
    Build more restrictive rules from exisiting list of files.
    """

    def __init__(
        self, printer: IConfigurationWriter, source_files: Iterator[SourceFile]
    ) -> None:
        app_configuration = AppConfigurationSingelton.get_instance()
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
            dependency_rules[build_module_regex(module)] = [
                build_rule(dependency) for dependency in dependencies
            ]

        self.printer.write(Configuration(dependency_rules))
