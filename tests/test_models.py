"""
Test functions in models module.
"""
import re

from dep_check.models import Module, build_module_regex, build_rule, get_parent


class TestBuildModuleRegex:
    """
    Test build module regex function.
    """

    @staticmethod
    def test_empty() -> None:
        """
        Test empty case.
        """
        # Given
        module = Module("")

        # When
        regex = build_module_regex(module)

        # Then
        assert regex == ""

    @staticmethod
    def test_simple_module() -> None:
        """
        Test simple case.
        """
        # Given
        module = Module("toto")

        # When
        regex = build_module_regex(module)

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
        module = Module("toto.tata")

        # When
        regex = build_module_regex(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "tata")
        assert not re.match(regex, "titi.toto")


class TestBuildRule:
    """
    Test build_rule function.
    """

    @staticmethod
    def test_empty() -> None:
        """
        Test empty case.
        """
        # Given
        module = Module("")

        # When
        regex = build_rule(module)

        # Then
        assert regex == ""

    @staticmethod
    def test_simple_module() -> None:
        """
        Test simple case.
        """
        # Given
        module = Module("toto")

        # When
        regex = build_rule(module)

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
        module = Module("toto.tata")

        # When
        regex = build_rule(module)

        # Then
        assert re.match(regex, "toto.tata")
        assert not re.match(regex, "toto")
        assert not re.match(regex, "tata")
        assert not re.match(regex, "titi.toto")


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
