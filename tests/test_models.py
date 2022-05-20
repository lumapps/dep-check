"""
Test functions in models module.
"""

from pytest import raises

from dep_check.models import Module, get_parent, iter_all_modules

from .fakefile import GLOBAL_DEPENDENCIES


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
        all_modules = []
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
