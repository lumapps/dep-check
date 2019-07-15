"""
Tests about find_dependencies function.
"""
from dep_check.dependency_finder import find_dependencies, find_import_from_dependencies
from dep_check.models import Dependency, Module, SourceCode, SourceFile

_SIMPLE_CASE = """
import simple
import module.inside.module
from amodule import aclass
"""
_SIMPLE_RESULT = frozenset(
    (
        Dependency(Module("simple")),
        Dependency(Module("amodule")),
        Dependency(Module("module.inside.module")),
    )
)
_SIMPLE_RESULT_IMPORT_FROM = frozenset(
    (
        Dependency(Module("simple")),
        Dependency(Module("amodule"), frozenset((Module("aclass"),))),
        Dependency(Module("module.inside.module")),
    )
)

_LOCAL_CASE = """
import simple
from . import aclass
from .inside.module import aclass
"""
_LOCAL_RESULT = set(
    (
        Dependency(Module("simple")),
        Dependency(Module("module")),
        Dependency(Module("module.inside.module")),
    )
)
_LOCAL_RESULT_IMPORT_FROM = set(
    (
        Dependency(Module("simple")),
        Dependency(Module("module"), frozenset((Module("aclass"),))),
        Dependency(Module("module.inside.module"), frozenset((Module("aclass"),))),
    )
)


class TestFindDependencies:
    @staticmethod
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
        assert dependencies == frozenset()

    @staticmethod
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

    @staticmethod
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


class TestFindImportFromDependencies:
    @staticmethod
    def test_empty() -> None:
        """
        Test empty code case.
        """
        # Given
        module = Module("")
        source_code = SourceCode("")
        source_file = SourceFile(module=module, code=source_code)

        # When
        dependencies = find_import_from_dependencies(source_file)

        # Then
        assert dependencies == frozenset()

    @staticmethod
    def test_simple_case() -> None:
        """
        Test simple code case.
        """
        # Given
        module = Module("toto_program")
        source_file = SourceFile(module=module, code=SourceCode(_SIMPLE_CASE))

        # When
        dependencies = find_import_from_dependencies(source_file)

        # Then
        assert dependencies == _SIMPLE_RESULT_IMPORT_FROM

    @staticmethod
    def test_local_import_case() -> None:
        """
        Test code with local import case.
        """
        # Given
        module = Module("module.toto")
        source_file = SourceFile(module=module, code=SourceCode(_LOCAL_CASE))

        # When
        dependencies = find_import_from_dependencies(source_file)

        # Then
        assert dependencies == _LOCAL_RESULT_IMPORT_FROM

    @staticmethod
    def test_multi_imports_after_from() -> None:
        # Given
        module = Module("module.toto")
        source_file = SourceFile(
            module=module,
            code=SourceCode("from module import amodule, othermodule, moduleagain"),
        )

        # When
        dependencies = find_import_from_dependencies(source_file)

        # Then
        assert dependencies == set(
            (
                Dependency(
                    Module("module"),
                    frozenset(
                        (
                            Module("amodule"),
                            Module("othermodule"),
                            Module("moduleagain"),
                        )
                    ),
                ),
            )
        )
