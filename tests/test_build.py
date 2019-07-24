"""
Test build configuration use case.
"""

from typing import Iterator
from unittest.mock import Mock

from dep_check.infra.python_parser import PythonParser
from dep_check.models import ModuleWildcard, SourceFile
from dep_check.use_cases.build import BuildConfigurationUC
from dep_check.use_cases.interfaces import Configuration

PARSER = PythonParser()


def test_empty() -> None:
    """
    Test result with no source files given.
    """
    # Given
    source_files: Iterator[SourceFile] = iter([])
    dependencies_writer = Mock()
    use_case = BuildConfigurationUC(dependencies_writer, PARSER, source_files, "python")

    # When
    use_case.run()

    # Then
    dependencies_writer.write.assert_called_with(Configuration())


def test_nominal(source_files) -> None:
    """
    Test result with a set source files.
    """
    # Given
    dependencies_writer = Mock()
    use_case = BuildConfigurationUC(dependencies_writer, PARSER, source_files, "python")

    # When
    use_case.run()

    # Then
    dependencies_writer.write.assert_called()  # type: ignore
    configuration = dependencies_writer.write.call_args[0][0]
    assert not configuration.local_init
    dependency_rules = {
        module_regex: set(rules)
        for module_regex, rules in configuration.dependency_rules.items()
    }
    assert dependency_rules == {
        "simple_module": set(
            (
                ModuleWildcard("module"),
                ModuleWildcard("module.inside.module"),
                ModuleWildcard("amodule"),
            )
        ),
        "amodule.local_module": set(
            (
                ModuleWildcard("module"),
                ModuleWildcard("module.inside.module"),
                ModuleWildcard("amodule"),
                ModuleWildcard("amodule.inside"),
            )
        ),
        "amodule.std_module": set(
            (ModuleWildcard("module"), ModuleWildcard("module.inside.module"))
        ),
    }
