"""
Test check use case.
"""

from unittest.mock import Mock

import pytest
from ordered_set import OrderedSet

from dep_check.infra.python_parser import PythonParser
from dep_check.models import Module, ModuleWildcard, SourceCode, SourceFile
from dep_check.use_cases.check import (
    CheckDependenciesUC,
    DependencyError,
    ForbiddenDepencyError,
    ForbiddenUnusedRuleError,
)
from dep_check.use_cases.interfaces import Configuration, UnusedLevel

from .fakefile import FILE_WITH_LOCAL_IMPORT, FILE_WITH_STD_IMPORT, SIMPLE_FILE

PARSER = PythonParser()


def test_empty_rules(source_files) -> None:
    """
    Test result with no rule given.
    """
    # Given
    configuration = Configuration()
    report_printer = Mock()
    use_case = CheckDependenciesUC(configuration, report_printer, PARSER, source_files)

    # When
    with pytest.raises(ForbiddenDepencyError):
        use_case.run()

    # Then
    assert OrderedSet(report_printer.print_report.call_args[0][0]) == OrderedSet(
        (
            DependencyError(SIMPLE_FILE.module, Module("module"), tuple()),
            DependencyError(
                SIMPLE_FILE.module, Module("module.inside.module"), tuple()
            ),
            DependencyError(SIMPLE_FILE.module, Module("amodule.aclass"), tuple()),
            DependencyError(FILE_WITH_LOCAL_IMPORT.module, Module("module"), tuple()),
            DependencyError(
                FILE_WITH_LOCAL_IMPORT.module, Module("module.inside.module"), tuple()
            ),
            DependencyError(
                FILE_WITH_LOCAL_IMPORT.module, Module("amodule.aclass"), tuple()
            ),
            DependencyError(
                FILE_WITH_LOCAL_IMPORT.module, Module("amodule.inside.aclass"), tuple()
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
            SIMPLE_FILE.module: [ModuleWildcard("module%"), ModuleWildcard("amodule")],
            "amodule.*": [
                ModuleWildcard("module"),
                ModuleWildcard("module.inside.*"),
                ModuleWildcard("amodule%"),
                ModuleWildcard("unused%"),
            ],
            "unused_wildcard.*": [ModuleWildcard("unused%")],
        }
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(configuration, report_printer, PARSER, source_files)

    # When
    use_case.run()

    # Then
    report_printer.print_report.assert_called_with(
        [],
        {
            (ModuleWildcard("amodule.*"), ModuleWildcard("unused%")),
            (ModuleWildcard("unused_wildcard.*"), ModuleWildcard("unused%")),
        },
        3,
    )


def test_error_on_unused(source_files) -> None:
    """
    Test result with a set rules that accept files.
    """
    # Given
    configuration = Configuration(
        dependency_rules={
            SIMPLE_FILE.module: [ModuleWildcard("module%"), ModuleWildcard("amodule")],
            "amodule.*": [
                ModuleWildcard("module"),
                ModuleWildcard("module.inside.*"),
                ModuleWildcard("amodule%"),
                ModuleWildcard("unused%"),
            ],
            "unused_wildcard.*": [ModuleWildcard("unused%")],
        },
        unused_level=UnusedLevel.ERROR.value,
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(configuration, report_printer, PARSER, source_files)

    # When
    with pytest.raises(ForbiddenUnusedRuleError):
        use_case.run()

    # Then
    report_printer.print_report.assert_called_with(
        [],
        {
            (ModuleWildcard("amodule.*"), ModuleWildcard("unused%")),
            (ModuleWildcard("unused_wildcard.*"), ModuleWildcard("unused%")),
        },
        3,
    )


def test_not_passing_rules(source_files) -> None:
    """
    Test result with a set rules that not accept files.
    """
    # Given
    dep_rules = {
        "simple_module": [ModuleWildcard("module.*"), ModuleWildcard("amodule")],
        "amodule.local_module": [
            ModuleWildcard("module"),
            ModuleWildcard("module.inside.*"),
            ModuleWildcard("amod"),
        ],
        "amodule.std_module": [ModuleWildcard("mod")],
    }

    configuration = Configuration(dependency_rules=dep_rules)
    report_printer = Mock()
    use_case = CheckDependenciesUC(configuration, report_printer, PARSER, source_files)

    # When
    with pytest.raises(ForbiddenDepencyError):
        use_case.run()

    # Then
    simple = SIMPLE_FILE.module
    local = FILE_WITH_LOCAL_IMPORT.module
    std = FILE_WITH_STD_IMPORT.module

    assert OrderedSet(report_printer.print_report.call_args[0][0]) == OrderedSet(
        (
            DependencyError(
                simple, Module("module"), tuple(sorted(dep_rules["simple_module"]))
            ),
            DependencyError(
                local,
                Module("amodule.aclass"),
                tuple(sorted(dep_rules["amodule.local_module"])),
            ),
            DependencyError(
                local,
                Module("amodule.inside.aclass"),
                tuple(sorted(dep_rules["amodule.local_module"])),
            ),
            DependencyError(
                std, Module("module"), tuple(sorted(dep_rules["amodule.std_module"]))
            ),
            DependencyError(
                std,
                Module("module.inside.module"),
                tuple(sorted(dep_rules["amodule.std_module"])),
            ),
        )
    )


def test_passing_rules_with_import_from() -> None:
    """
    Test result with a set rules that accept files.
    """
    # Given
    configuration = Configuration(
        dependency_rules={
            "module": [ModuleWildcard("module%"), ModuleWildcard("amodule.submodule")]
        }
    )
    source_file = SourceFile(
        Module("module"), SourceCode("from amodule import submodule")
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration, report_printer, PARSER, iter([source_file])
    )

    # When
    use_case.run()

    # Then
    assert report_printer.print_report.call_args[0][0] == []


def test_not_passing_rules_with_import_from() -> None:
    """
    Test result with a set rules that accept files.
    """
    # Given
    dep_rules = {
        "module": [ModuleWildcard("module%"), ModuleWildcard("amodule.submodule")]
    }
    configuration = Configuration(dep_rules)
    source_file = SourceFile(
        Module("module"), SourceCode("from amodule import othermodule, submodule\n")
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration, report_printer, PARSER, iter([source_file])
    )

    # When
    with pytest.raises(ForbiddenDepencyError):
        use_case.run()

    # Then
    assert OrderedSet(report_printer.print_report.call_args[0][0]) == OrderedSet(
        (
            DependencyError(
                Module("module"),
                Module("amodule.othermodule"),
                tuple(sorted(dep_rules["module"])),
            ),
        )
    )


def test_passing_dynamic_rule() -> None:
    # Given
    dep_rules = {
        "module_(<name>*)": [
            ModuleWildcard("module.{name}%"),
            ModuleWildcard("{name}.submodule"),
        ]
    }
    configuration = Configuration(dep_rules)
    source_file_toto = SourceFile(
        Module("module_toto"),
        SourceCode(
            "from toto import submodule\nfrom module.toto import what_ever, other\n"
        ),
    )
    source_file_tata = SourceFile(
        Module("module_tata"),
        SourceCode(
            "from tata import submodule\nfrom module.tata import what_ever, other\n"
        ),
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration,
        report_printer,
        PARSER,
        iter([source_file_toto, source_file_tata]),
    )

    # When
    use_case.run()

    # Then
    assert report_printer.print_report.call_args[0][0] == []


def test_not_passing_dynamic_rule() -> None:
    # Given
    dep_rules = {
        "module_(<name>*)": [
            ModuleWildcard("module.{name}%"),
            ModuleWildcard("{name}.submodule"),
        ]
    }
    configuration = Configuration(dep_rules)
    source_file_toto = SourceFile(
        Module("module_toto"),
        SourceCode("from tata import submodule\n"),
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration,
        report_printer,
        PARSER,
        iter([source_file_toto]),
    )

    # When
    with pytest.raises(ForbiddenDepencyError):
        use_case.run()

    # Then
    assert OrderedSet(report_printer.print_report.call_args[0][0]) == OrderedSet(
        (
            DependencyError(
                Module("module_toto"),
                Module("tata.submodule"),
                (ModuleWildcard("module.toto%"), ModuleWildcard("toto.submodule")),
            ),
        )
    )


def test_not_used_dynamic_rule() -> None:
    # Given
    dep_rules = {
        "module_(<name>*)": [
            ModuleWildcard("module%"),
            ModuleWildcard("{name}.submodule"),
        ]
    }
    configuration = Configuration(dep_rules)
    source_file_toto = SourceFile(
        Module("module_toto"),
        SourceCode(
            "from toto import submodule\nfrom module.toto import what_ever, other\n"
        ),
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration,
        report_printer,
        PARSER,
        iter([source_file_toto]),
    )

    # When
    use_case.run()

    # Then
    assert report_printer.print_report.call_args[0][0] == []


def test_passing_inverted_rule() -> None:
    # Given
    dep_rules = {
        "foo": [
            ModuleWildcard("bar%"),
            ModuleWildcard("~bar.baz"),
        ]
    }
    configuration = Configuration(dep_rules)
    source_file = SourceFile(
        Module("foo"),
        SourceCode("import bar\nfrom bar import submodule\n"),
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration,
        report_printer,
        PARSER,
        iter([source_file]),
    )

    # When
    use_case.run()

    # Then
    assert not report_printer.print_report.call_args[0][0]


def test_not_passing_inverted_rule() -> None:
    # Given
    dep_rules = {
        "foo": [
            ModuleWildcard("bar%"),
            ModuleWildcard("~bar.baz%"),
        ]
    }
    configuration = Configuration(dep_rules)
    source_file = SourceFile(
        Module("foo"),
        SourceCode("import bar\nfrom bar import baz\n"),
    )
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration,
        report_printer,
        PARSER,
        iter([source_file]),
    )

    # When
    with pytest.raises(ForbiddenDepencyError):
        use_case.run()

    # Then
    assert report_printer.print_report.call_args[0][0] == OrderedSet(
        (
            DependencyError(
                module=Module("foo"),
                dependency=Module("bar.baz"),
                rules=(ModuleWildcard("bar%"), ModuleWildcard("~bar.baz%")),
            ),
        )
    )


def test_passing_inverted_no_unused_rule() -> None:
    # Given
    dep_rules = {
        "foo": [
            ModuleWildcard("bar%"),
            ModuleWildcard("~baz%"),
        ]
    }
    configuration = Configuration(dep_rules, unused_level=UnusedLevel.ERROR.value)
    source_file = SourceFile(Module("foo"), SourceCode("import bar"))
    report_printer = Mock()
    use_case = CheckDependenciesUC(
        configuration,
        report_printer,
        PARSER,
        iter([source_file]),
    )

    # When
    use_case.run()

    # Then
    assert not report_printer.print_report.call_args[0][0]
