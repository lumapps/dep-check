"""
Test check use case.
"""
from typing import List

from pytest import raises

from dep_check.checker import NotAllowedDependencyException, check_dependency
from dep_check.infra.python_parser import PythonParser
from dep_check.models import Dependency, Module, ModuleWildcard, Rules

PARSER = PythonParser()


def test_empty() -> None:
    """
    Test empty rules case.
    """
    # Given
    dependency = Dependency(Module("toto"))
    authorized_modules: List[ModuleWildcard] = []

    # When
    with raises(NotAllowedDependencyException) as error:
        check_dependency(PARSER, dependency, authorized_modules)

    # Then
    assert error
    assert error.value.dependency == dependency.main_import
    assert error.value.authorized_modules == authorized_modules


def test_passing_case() -> None:
    """
    Test a passing case.
    """
    # Given
    dependency = Dependency(Module("toto"))
    rules: Rules = [
        (ModuleWildcard("toto"), ModuleWildcard("to*")),
        (ModuleWildcard("toto"), ModuleWildcard("titi.tata")),
    ]

    # When
    error = None
    try:
        check_dependency(PARSER, dependency, rules)
    except NotAllowedDependencyException as exception:
        error = exception

    # Then
    assert not error


def test_not_passing_case() -> None:
    """
    Test a not passing case.
    """
    # Given
    dependency = Dependency(Module("toto.tata"))
    rules: Rules = [
        (ModuleWildcard("toto.*"), ModuleWildcard("toto")),
        (ModuleWildcard("toto.*"), ModuleWildcard("te.*")),
        (ModuleWildcard("toto.*"), ModuleWildcard("titi\\.tata")),
    ]

    # When
    with raises(NotAllowedDependencyException) as error:
        check_dependency(PARSER, dependency, rules)

    # Then
    assert error
    assert error.value.dependency == dependency.main_import
    assert error.value.authorized_modules == [r for _, r in rules]
