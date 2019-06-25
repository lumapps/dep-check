"""
Tests about find_dependencies function.
"""
from dep_check.dependency_finder import find_dependencies
from dep_check.models import Module, SourceCode, SourceFile


def test_empty() -> None:
    """
    Test empty code case.
    """
    # Given
    module = Module("")
    source_code = SourceCode("")
    source_file = SourceFile(module=module, code=source_code)

    # When
    dependencies = find_dependencies(source_file)

    # Then
    assert dependencies == set()


_SIMPLE_CASE = """
import simple
import module.inside.module
from amodule import aclass
"""
_SIMPLE_RESULT = set(
    (Module("simple"), Module("amodule"), Module("module.inside.module"))
)


def test_simple_case() -> None:
    """
    Test simple code case.
    """
    # Given
    module = Module("toto_program")
    source_file = SourceFile(module=module, code=SourceCode(_SIMPLE_CASE))

    # When
    dependencies = find_dependencies(source_file)

    # Then
    assert dependencies == _SIMPLE_RESULT


_LOCAL_CASE = """
import simple
from . import aclass
from .inside.module import aclass
"""
_LOCAL_RESULT = set(
    (Module("simple"), Module("module"), Module("module.inside.module"))
)


def test_local_import_case() -> None:
    """
    Test code with local import case.
    """
    # Given
    module = Module("module.toto")
    source_file = SourceFile(module=module, code=SourceCode(_LOCAL_CASE))

    # When
    dependencies = find_dependencies(source_file)

    # Then
    assert dependencies == _LOCAL_RESULT
