"""
Tests about get_dependencies function.
"""
import re

from dep_check.dependency_finder import get_dependencies, get_import_from_dependencies
from dep_check.infra.python_parser import PythonParser
from dep_check.models import Dependency, Module, ModuleWildcard, SourceCode, SourceFile

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

PARSER = PythonParser()


class TestGetDependencies:
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
        dependencies = get_dependencies(source_file, PARSER)

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
        dependencies = get_dependencies(source_file, PARSER)

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
        dependencies = get_dependencies(source_file, PARSER)

        # Then
        assert dependencies == _LOCAL_RESULT


class TestGetImportFromDependencies:
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
        dependencies = get_import_from_dependencies(source_file, PARSER)

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
        dependencies = get_import_from_dependencies(source_file, PARSER)

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
        dependencies = get_import_from_dependencies(source_file, PARSER)

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
        dependencies = get_import_from_dependencies(source_file, PARSER)

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


class TestRegexToWildcard:
    """
    Test build module regex function.
    """

    @staticmethod
    def test_empty() -> None:
        """
        Test empty case.
        """
        # Given
        module = ModuleWildcard("")

        # When
        regex = PARSER.wildcard_to_regex(module)

        # Then
        assert regex == ""

    @staticmethod
    def test_simple_module() -> None:
        """
        Test simple case.
        """
        # Given
        module = ModuleWildcard("toto")

        # When
        regex = PARSER.wildcard_to_regex(module)

        # Then
        assert re.match(regex, "toto")
        assert not re.match(regex, "tata")
        assert not re.match(regex, "titi.toto")

    @staticmethod
    def test_nested_module() -> None:
        """
        Test nested case.
        """
        # Given
        module = ModuleWildcard("toto.tata")

        # When
        regex = PARSER.wildcard_to_regex(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "tata")
        assert not re.match(regex, "titi.toto")

    @staticmethod
    def test_quesiton_mark() -> None:
        """
        Test question mark case
        """
        # Given
        module = ModuleWildcard("t?to.?at?")

        # When
        regex = PARSER.wildcard_to_regex(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert re.match(regex, "t2to.bato")
        assert re.match(regex, "t#to.!at&")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "tata")
        assert not re.match(regex, "toti.toto")

    @staticmethod
    def test_asterisk() -> None:
        """
        Test asterisk case
        """
        # Given
        module = ModuleWildcard("toto*.*")

        # When
        regex = PARSER.wildcard_to_regex(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert re.match(regex, "toto_2351.titi")
        assert re.match(regex, "toto_azerty.titi.toto.tata")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "tototata")
        assert not re.match(regex, "toti.toto")

    @staticmethod
    def test_percentage() -> None:
        """
        Test percentage case
        """
        # Given
        module = ModuleWildcard("toto.tata%")

        # When
        regex = PARSER.wildcard_to_regex(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert re.match(regex, "toto.tata.titi")
        assert re.match(regex, "toto.tata.titi.tutu.tototata.tititutu")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "toto.tata_123")
