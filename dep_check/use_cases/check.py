"""
Check all given source files dependencies use case.
"""


import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, List, Tuple

from dep_check.checker import NotAllowedDependencyException, check_dependency
from dep_check.dependency_finder import IParser, get_import_from_dependencies
from dep_check.models import Module, ModuleWildcard, Rules, SourceFile

from .app_configuration import AppConfigurationSingleton
from .interfaces import Configuration


class ForbiddenError(Exception):
    pass


class ForbiddenUnusedRuleError(ForbiddenError):
    pass


class ForbiddenDepencyError(ForbiddenError):
    pass


@dataclass(frozen=True)
class DependencyError:
    """
    Dataclass representing a dependency error.
    """

    module: Module
    dependency: Module
    rules: Tuple[ModuleWildcard, ...]


class IReportPrinter(ABC):
    """
    Errors printer interface.
    """

    @abstractmethod
    def _error(self, dep_errors: List[DependencyError]) -> None:
        """
        Display errors.
        """

    @abstractmethod
    def _warning(self, unused_rules: Rules) -> None:
        """
        Display warnings.
        """

    @abstractmethod
    def print_report(
        self, errors: List[DependencyError], unused_rules: Rules, nb_files: int
    ) -> None:
        """
        Print report
        """


class CheckDependenciesUC:
    """
    Dependency check use case.

    In this use case, we ensure that all given source files respect
    all rules that matching their module name.
    """

    def __init__(
        self,
        configuration: Configuration,
        report_printer: IReportPrinter,
        parser: IParser,
        source_files: Iterator[SourceFile],
    ):
        app_configuration = AppConfigurationSingleton.get_instance()
        self.std_lib_filter = app_configuration.std_lib_filter
        self.configuration = configuration
        self.report_printer = report_printer
        self.parser = parser
        self.source_files = source_files
        self.used_rules: Rules = set()
        self.all_rules: Rules = set()

    def _get_rules(self, module: Module) -> Rules:
        """
        Return rules in configuration that match a given module.
        """
        matching_rules: Rules = set()
        for module_wildcard, rules in self.configuration.dependency_rules.items():
            if re.match(
                f"{self.parser.wildcard_to_regex(ModuleWildcard(module_wildcard))}$",
                module,
            ):
                matching_rules.update(
                    (ModuleWildcard(module_wildcard), r) for r in rules
                )

        return matching_rules

    def _iter_error(self, source_file: SourceFile) -> Iterator[DependencyError]:
        rules = self._get_rules(source_file.module)
        self.all_rules.update(set(rules))
        dependencies = get_import_from_dependencies(source_file, self.parser)
        dependencies = self.std_lib_filter.filter(dependencies)
        for dependency in dependencies:
            try:
                self.used_rules |= check_dependency(self.parser, dependency, rules)
            except NotAllowedDependencyException as error:
                yield DependencyError(
                    source_file.module,
                    error.dependency,
                    tuple(sorted(error.authorized_modules)),
                )

    def run(self) -> None:
        errors = []
        nb_files = 0

        for source_file in self.source_files:
            nb_files += 1
            for error in self._iter_error(source_file):
                errors.append(error)

        unused = self.all_rules.difference(self.used_rules)
        self.report_printer.print_report(errors, unused, nb_files)

        if self.configuration.error_on_unused and unused:
            raise ForbiddenUnusedRuleError

        if errors:
            raise ForbiddenDepencyError
