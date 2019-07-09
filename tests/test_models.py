"""
Test functions in models module.
"""
import re

from pytest import raises

from dep_check.models import (
    Module,
    ModuleWildcard,
    get_parent,
    iter_all_modules,
    wildcard_to_regex,
)

from .fakefile import GLOBAL_DEPENDENCIES


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
        regex = wildcard_to_regex(module)

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
        regex = wildcard_to_regex(module)

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
        regex = wildcard_to_regex(module)

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
        regex = wildcard_to_regex(module)

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
        regex = wildcard_to_regex(module)

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
        regex = wildcard_to_regex(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert re.match(regex, "toto.tata.titi")
        assert re.match(regex, "toto.tata.titi.tutu.tototata.tititutu")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "toto.tata_123")


class TestGetParent:
    """
    Test get_parent function.
    """

    @staticmethod
    def test_empty() -> None:
        """
        Test empty case.
        """
        # Given
        module = Module("")

        # When
        parent = get_parent(module)

        # Then
        assert parent == ""

    @staticmethod
    def test_simple_module() -> None:
        """
        Test simple case.
        """
        # Given
        module = Module("toto")

        # When
        parent = get_parent(module)

        # Then
        assert parent == Module("")

    @staticmethod
    def test_nested_module() -> None:
        """
        Test nested case.
        """
        # Given
        module = Module("toto.tata")

        # When
        parent = get_parent(module)

        # Then
        assert parent == Module("toto")

    @staticmethod
    def test_long_nested_module() -> None:
        """
        Test long nested case.
        """
        # Given
        module = Module("toto.titi.tete.tata")

        # When
        parent = get_parent(module)

        # Then
        assert parent == Module("toto.titi.tete")


class TestIterAllModules:
    """
    Test iter_all_modules function
    """

    @staticmethod
    def test_empty() -> None:
        """
        Test empty case.
        """
        # Given
        global_deps = {}

        # When
        result_iter = iter_all_modules(global_deps)

        # Then
        with raises(StopIteration):
            next(result_iter)

    @staticmethod
    def test_nominal() -> None:
        """
        Test nominal case.
        """
        # Given
        global_deps = GLOBAL_DEPENDENCIES

        # When
        result_iter = iter_all_modules(global_deps)

        # Then
        all_modules = list()
        for module in result_iter:
            all_modules.append(module)

        assert sorted(all_modules) == sorted(
            [
                "simple_module",
                "module",
                "module.inside.module",
                "amodule",
                "amodule.local_module",
                "amodule.inside",
                "amodule.std_module",
            ]
        )
