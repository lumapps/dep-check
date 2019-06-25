"""
Test build configuration use case.
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
from dep_check.use_cases.build import BuildConfigurationUC
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


def test_nominal() -> None:
    """
    Test result with a set source files.
    """
    # Given
    source_files = get_source_file_iterator()
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
            (Rule("module"), Rule(r"module\.inside\.module"), Rule("amodule"))
        ),
        r"amodule\.local_module": set(
            (
                Rule("module"),
                Rule(r"module\.inside\.module"),
                Rule("amodule"),
                Rule(r"amodule\.inside"),
            )
        ),
        r"amodule\.std_module": set((Rule("module"), Rule(r"module\.inside\.module"))),
    }
