"""
Check all given source files dependencies use case.
"""


import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, List, Tuple

from dep_check.checker import NotAllowedDependencyException, check_dependency
from dep_check.dependency_finder import find_dependencies
from dep_check.models import Module, Rule, Rules, SourceFile, build_rule, get_parent

from .app_configuration import AppConfigurationSingelton
from .interfaces import Configuration, ExitCode


class IConfigurationReader(ABC):
    """
    Configuration reader interface.
    """

    @abstractmethod
    def read(self) -> Configuration:
        """
        Read configuration for a source.
        """


@dataclass(frozen=True)
class DependencyError:
    """
    Dataclass representing a dependency error.
    """

    module: Module
    dependency: Module
    rules: Tuple[Rule, ...]


class IErrorPrinter(ABC):
    """
    Errors printer interface.
    """

    @abstractmethod
    def print(self, errors: List[DependencyError]) -> None:
        """
        Print errors.
        """


class CheckDependenciesUC:
    """
    Dependency check use case.

    In this use case, we ensure that all given source files respect
    all rules that matching their module name.
    """

    def __init__(
        self,
        configuration_reader: IConfigurationReader,
        error_printer: IErrorPrinter,
        source_files: Iterator[SourceFile],
    ):
        app_configuration = AppConfigurationSingelton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.configuration = configuration_reader.read()
        self.error_printer = error_printer
        self.source_files = source_files

    def _get_rules(self, module: Module) -> Rules:
        """
        Return rules in configuration that match a given module.
        """
        if self.configuration.local_init and module.endswith(".__init__"):
            parent_module_regex = build_rule(get_parent(module))
            return [Rule(r"{}.*".format(parent_module_regex))]

        matching_rules: Rules = []
        for module_regex, rules in self.configuration.dependency_rules.items():
            if re.match("{}$".format(module_regex), module):
                matching_rules.extend(rules)

        return matching_rules

    def _iter_error(self, source_file: SourceFile) -> Iterator[DependencyError]:
        rules = self._get_rules(source_file.module)
        dependencies = find_dependencies(source_file)
        dependencies = self.std_lib_filter.filter(dependencies)
        for dependency in dependencies:
            try:
                check_dependency(dependency, rules)
            except NotAllowedDependencyException:
                yield DependencyError(source_file.module, dependency, tuple(rules))

    def run(self) -> ExitCode:
        errors = [
            error
            for source_file in self.source_files
            for error in self._iter_error(source_file)
        ]
        self.error_printer.print(errors)
        return ExitCode.OK if not errors else ExitCode.KO
