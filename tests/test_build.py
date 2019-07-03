"""
Test build configuration use case.
"""

from typing import Iterator
from unittest.mock import Mock

from dep_check.models import  Rule, SourceFile
from dep_check.use_cases.build import BuildConfigurationUC
from dep_check.use_cases.interfaces import Configuration

def test_empty() -> None:
    """
    Test result with no source files given.
    """
    # Given
    source_files: Iterator[SourceFile] = iter([])
    dependencies_writer = Mock()
    use_case = BuildConfigurationUC(dependencies_writer, source_files)

    # When
    use_case.run()

    # Then
    dependencies_writer.write.assert_called_with(Configuration())


def test_nominal(get_source_file_iterator) -> None:
    """
    Test result with a set source files.
    """
    # Given
    source_files = get_source_file_iterator
    dependencies_writer = Mock()
    use_case = BuildConfigurationUC(dependencies_writer, source_files)

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
            (Rule("module"), Rule("module.inside.module"), Rule("amodule"))
        ),
        "amodule.local_module": set(
            (
                Rule("module"),
                Rule("module.inside.module"),
                Rule("amodule"),
                Rule("amodule.inside"),
            )
        ),
        "amodule.std_module": set((Rule("module"), Rule("module.inside.module"))),
    }
