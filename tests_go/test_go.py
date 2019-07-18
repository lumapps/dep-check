from dep_check.dependency_finder import get_dependencies
from dep_check.infra.go_parser import GoParser
from dep_check.models import Dependency, Module, SourceCode, SourceFile

PARSER = GoParser()


def test_empty() -> None:
    """
    Test empty code case.
    """
    # Given
    module = Module("")
    source_code = SourceCode("")
    source_file = SourceFile(module=module, code=source_code)

    # When
    dependencies = get_dependencies(source_file, PARSER)

    # Then
    assert dependencies == frozenset()


def test_nominal() -> None:
    source_file = SourceFile(
        Module("string.string"),
        SourceCode(
            """package main
    import "fmt"
    import (
        "go/parser"
        "go/module"
        "othermodule"
    )
    import "amodule"
    """
        ),
    )

    assert get_dependencies(source_file, PARSER) == {
        Dependency("fmt"),
        Dependency("go/parser"),
        Dependency("go/module"),
        Dependency("othermodule"),
        Dependency("amodule"),
    }
