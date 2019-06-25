"""
Test check use case.
"""

from typing import Iterator
from unittest.mock import Mock

from dep_check.infra.std_lib_filter import StdLibSimpleFilter
from dep_check.models import Module, Rule, SourceCode, SourceFile
from dep_check.use_cases.app_configuration import (
    AppConfiguration,
    AppConfigurationAlreadySetException,
    AppConfigurationSingelton,
)
from dep_check.use_cases.check import CheckDependenciesUC, DependencyError, IConfigurationReader
from dep_check.use_cases.interfaces import Configuration

_SIMPLE_FILE = SourceFile(
    module=Module("simple_module"),
    code=SourceCode(
        """
import module
import module.inside.module
from amodule import aclass
"""
    ),
)
_FILE_WITH_LOCAL_IMPORT = SourceFile(
    module=Module("amodule.local_module"),
    code=SourceCode(
        """
import module
import module.inside.module
from . import aclass
from .inside import aclass
"""
    ),
)
_FILE_WITH_STD_IMPORT = SourceFile(
    module=Module("amodule.std_module"),
    code=SourceCode(
        """
import module
import module.inside.module
import itertools
from abc import ABC
"""
    ),
)


def setup_module() -> None:
    """
    Define application configuration.
    """
    app_configuration = AppConfiguration(std_lib_filter=StdLibSimpleFilter())
    try:
        AppConfigurationSingelton.define_app_configuration(app_configuration)
    except AppConfigurationAlreadySetException:
        pass


def get_source_file_iterator() -> Iterator[SourceFile]:
    """
    Iter over test source files.
    """
    yield _SIMPLE_FILE
    yield _FILE_WITH_LOCAL_IMPORT
    yield _FILE_WITH_STD_IMPORT


def build_conf_reader_stub(configuration: Configuration) -> IConfigurationReader:
    """
    Create a ConfigurationReader stub.
    """
    attrs = {"read.return_value": configuration}
    return Mock(**attrs)


def test_empty_rules() -> None:
    """
    Test result with no rule given.
    """
    # Given
    source_files = get_source_file_iterator()
    configuration = Configuration()
    configuration_reader = build_conf_reader_stub(configuration)
    error_printer = Mock()
    use_case = CheckDependenciesUC(configuration_reader, error_printer, source_files)

    # When
    use_case.run()

    # Then
    configuration_reader.read.assert_called()  # type: ignore
    error_printer.print.assert_called()  # type: ignore
    assert set(error_printer.print.call_args[0][0]) == set(
        (
            DependencyError(_SIMPLE_FILE.module, Module("module"), tuple()),
            DependencyError(
                _SIMPLE_FILE.module, Module("module.inside.module"), tuple()
            ),
            DependencyError(_SIMPLE_FILE.module, Module("amodule"), tuple()),
            DependencyError(_FILE_WITH_LOCAL_IMPORT.module, Module("module"), tuple()),
            DependencyError(
                _FILE_WITH_LOCAL_IMPORT.module, Module("module.inside.module"), tuple()
            ),
            DependencyError(_FILE_WITH_LOCAL_IMPORT.module, Module("amodule"), tuple()),
            DependencyError(
                _FILE_WITH_LOCAL_IMPORT.module, Module("amodule.inside"), tuple()
            ),
            DependencyError(_FILE_WITH_STD_IMPORT.module, Module("module"), tuple()),
            DependencyError(
                _FILE_WITH_STD_IMPORT.module, Module("module.inside.module"), tuple()
            ),
        )
    )


def test_passing_rules() -> None:
    """
    Test result with a set rules that accept files.
    """
    # Given
    source_files = get_source_file_iterator()
    configuration = Configuration(
        dependency_rules={
            _SIMPLE_FILE.module: [Rule("module.*"), Rule("amodule")],
            r"amodule\..*": [
                Rule("module"),
                Rule(r"module\.inside\..*"),
                Rule("amodule.*"),
            ],
        }
    )
    configuration_reader = build_conf_reader_stub(configuration)
    error_printer = Mock()
    use_case = CheckDependenciesUC(configuration_reader, error_printer, source_files)

    # When
    use_case.run()

    # Then
    configuration_reader.read.assert_called()  # type: ignore
    error_printer.print.assert_called_with([])


def test_not_passing_rules() -> None:
    """
    Test result with a set rules that not accept files.
    """
    # Given
    source_files = get_source_file_iterator()
    dep_rules = {
        "simple_module": [Rule(r"module\..*"), Rule("amodule")],
        r"amodule\.local_module": [
            Rule("module"),
            Rule(r"module\.inside\..*"),
            Rule("amod"),
        ],
        r"amodule\.std_module": [Rule("mod")],
    }

    configuration = Configuration(dependency_rules=dep_rules)
    configuration_reader = build_conf_reader_stub(configuration)
    error_printer = Mock()
    use_case = CheckDependenciesUC(configuration_reader, error_printer, source_files)

    # When
    use_case.run()

    # Then
    configuration_reader.read.assert_called()  # type: ignore
    error_printer.print.assert_called()  # type: ignore
    simple = _SIMPLE_FILE.module
    local = _FILE_WITH_LOCAL_IMPORT.module
    std = _FILE_WITH_STD_IMPORT.module

    assert set(error_printer.print.call_args[0][0]) == set(
        (
            DependencyError(
                simple, Module("module"), tuple(dep_rules["simple_module"])
            ),
            DependencyError(
                local, Module("amodule"), tuple(dep_rules[r"amodule\.local_module"])
            ),
            DependencyError(
                local,
                Module("amodule.inside"),
                tuple(dep_rules[r"amodule\.local_module"]),
            ),
            DependencyError(
                std, Module("module"), tuple(dep_rules[r"amodule\.std_module"])
            ),
            DependencyError(
                std,
                Module("module.inside.module"),
                tuple(dep_rules[r"amodule\.std_module"]),
            ),
        )
    )
