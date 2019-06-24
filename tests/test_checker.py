"""
Test check use case.
"""
from checker import NotAllowedDependencyException, check_dependency
from models import Module, Rule, Rules


def test_empty() -> None:
    """
    Test empty rules case.
    """
    # Given
    dependency = Module("toto")
    rules: Rules = []

    # When
    error = None
    try:
        check_dependency(dependency, rules)
    except NotAllowedDependencyException as exception:
        error = exception

    # Then
    assert error
    assert error.dependency == dependency
    assert error.rules == rules


def test_passing_case() -> None:
    """
    Test a passing case.
    """
    # Given
    dependency = Module("toto")
    rules: Rules = [Rule("to.*"), Rule("titi\\.tata")]

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
    rules: Rules = [Rule("toto"), Rule("te.*"), Rule("titi\\.tata")]

    # When
    error = None
    try:
        check_dependency(dependency, rules)
    except NotAllowedDependencyException as exception:
        error = exception

    # Then
    assert error
    assert error.dependency == dependency
    assert error.rules == rules
