"""
Test check use case.
"""

from unittest.mock import Mock

from dep_check.models import Module, Rule
from dep_check.use_cases.check import (
    CheckDependenciesUC,
    DependencyError,
    IConfigurationReader,
)
from dep_check.use_cases.interfaces import Configuration

from .fakefile import FILE_WITH_LOCAL_IMPORT, FILE_WITH_STD_IMPORT, SIMPLE_FILE


def build_conf_reader_stub(configuration: Configuration) -> IConfigurationReader:
    """
    Create a ConfigurationReader stub.
    """
    attrs = {"read.return_value": configuration}
    return Mock(**attrs)


def test_empty_rules(source_files) -> None:
    """
    Test result with no rule given.
    """
    # Given
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
            DependencyError(SIMPLE_FILE.module, Module("module"), tuple()),
            DependencyError(
                SIMPLE_FILE.module, Module("module.inside.module"), tuple()
            ),
            DependencyError(SIMPLE_FILE.module, Module("amodule"), tuple()),
            DependencyError(FILE_WITH_LOCAL_IMPORT.module, Module("module"), tuple()),
            DependencyError(
                FILE_WITH_LOCAL_IMPORT.module, Module("module.inside.module"), tuple()
            ),
            DependencyError(FILE_WITH_LOCAL_IMPORT.module, Module("amodule"), tuple()),
            DependencyError(
                FILE_WITH_LOCAL_IMPORT.module, Module("amodule.inside"), tuple()
            ),
            DependencyError(FILE_WITH_STD_IMPORT.module, Module("module"), tuple()),
            DependencyError(
                FILE_WITH_STD_IMPORT.module, Module("module.inside.module"), tuple()
            ),
        )
    )


def test_passing_rules(source_files) -> None:
    """
    Test result with a set rules that accept files.
    """
    # Given
    configuration = Configuration(
        dependency_rules={
            SIMPLE_FILE.module: [Rule("module%"), Rule("amodule")],
            "amodule.*": [Rule("module"), Rule("module.inside.*"), Rule("amodule%")],
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


def test_not_passing_rules(source_files) -> None:
    """
    Test result with a set rules that not accept files.
    """
    # Given
    dep_rules = {
        "simple_module": [Rule("module.*"), Rule("amodule")],
        "amodule.local_module": [Rule("module"), Rule("module.inside.*"), Rule("amod")],
        "amodule.std_module": [Rule("mod")],
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
    simple = SIMPLE_FILE.module
    local = FILE_WITH_LOCAL_IMPORT.module
    std = FILE_WITH_STD_IMPORT.module

    assert set(error_printer.print.call_args[0][0]) == set(
        (
            DependencyError(
                simple, Module("module"), tuple(dep_rules["simple_module"])
            ),
            DependencyError(
                local, Module("amodule"), tuple(dep_rules["amodule.local_module"])
            ),
            DependencyError(
                local,
                Module("amodule.inside"),
                tuple(dep_rules["amodule.local_module"]),
            ),
            DependencyError(
                std, Module("module"), tuple(dep_rules["amodule.std_module"])
            ),
            DependencyError(
                std,
                Module("module.inside.module"),
                tuple(dep_rules["amodule.std_module"]),
            ),
        )
    )
