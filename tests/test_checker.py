"""
Test check use case.
"""
from pytest import raises

from dep_check.checker import NotAllowedDependencyException, check_dependency
from dep_check.models import Module, ModuleWildcard, Rules


def test_empty() -> None:
    """
    Test empty rules case.
    """
    # Given
    dependency = Module("toto")
    rules: Rules = []

    # When
    with raises(NotAllowedDependencyException) as error:
        check_dependency(dependency, rules)

    # Then
    assert error
    assert error.value.dependency == dependency
    assert error.value.rules == rules


def test_passing_case() -> None:
    """
    Test a passing case.
    """
    # Given
    dependency = Module("toto")
    rules: Rules = [ModuleWildcard("to*"), ModuleWildcard("titi.tata")]

    # When
    error = None
    try:
        check_dependency(dependency, rules)
    except NotAllowedDependencyException as exception:
        error = exception

    # Then
    assert not error


def test_not_passing_case() -> None:
    """
    Test a not passing case.
    """
    # Given
    dependency = Module("toto.tata")
    rules: Rules = [
        ModuleWildcard("toto"),
        ModuleWildcard("te.*"),
        ModuleWildcard("titi\\.tata"),
    ]

    # When
    with raises(NotAllowedDependencyException) as error:
        check_dependency(dependency, rules)

    # Then
    assert error
    assert error.value.dependency == dependency
    assert error.value.rules == rules
