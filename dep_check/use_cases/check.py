"""
Check all given source files dependencies use case.
"""


import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, List, Tuple

from dep_check.checker import NotAllowedDependencyException, check_dependency
from dep_check.dependency_finder import find_import_from_dependencies
from dep_check.models import (
    Module,
    ModuleWildcard,
    Rules,
    SourceFile,
    get_parent,
    wildcard_to_regex,
)

from .app_configuration import AppConfigurationSingleton
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
    rules: Tuple[ModuleWildcard, ...]


class IErrorPrinter(ABC):
    """
    Errors printer interface.
    """

    @abstractmethod
    def print(self, errors: List[DependencyError]) -> None:
        """
        Print errors.
        """

    @abstractmethod
    def warn(self, unused_rules: Rules) -> None:
        """
        Print warnings.
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
        app_configuration = AppConfigurationSingleton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.configuration = configuration_reader.read()
        self.error_printer = error_printer
        self.source_files = source_files
        self.used_rules: Rules = set()
        self.all_rules: Rules = set()

    def _get_rules(self, module: Module) -> Rules:
        """
        Return rules in configuration that match a given module.
        """
        if self.configuration.local_init and module.endswith(".__init__"):
            parent_module = get_parent(module)
            return {
                (ModuleWildcard(module), ModuleWildcard(r"{}%".format(parent_module)))
            }

        matching_rules: Rules = set()
        for module_wildcard, rules in self.configuration.dependency_rules.items():
            if re.match(
                "{}$".format(wildcard_to_regex(ModuleWildcard(module_wildcard))), module
            ):
                matching_rules.update(
                    (ModuleWildcard(module_wildcard), r) for r in rules
                )

        return matching_rules

    def _iter_error(self, source_file: SourceFile) -> Iterator[DependencyError]:
        rules = self._get_rules(source_file.module)
        self.all_rules.update(set(rules))
        dependencies = find_import_from_dependencies(source_file)
        dependencies = self.std_lib_filter.filter(dependencies)
        for dependency in dependencies:
            try:
                self.used_rules |= check_dependency(dependency, rules)
            except NotAllowedDependencyException as error:
                yield DependencyError(
                    source_file.module,
                    error.dependency,
                    tuple(sorted(error.authorized_modules)),
                )

    def run(self) -> ExitCode:
        errors = [
            error
            for source_file in self.source_files
            for error in self._iter_error(source_file)
        ]
        self.error_printer.print(errors)

        unused = self.all_rules.difference(self.used_rules)
        if unused:
            self.error_printer.warn(unused)

        return ExitCode.OK if not errors else ExitCode.KO
