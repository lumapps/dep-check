from unittest.mock import Mock

from dep_check.use_cases.app_configuration import (
    AppConfigurationAlreadySetException,
    AppConfigurationSingleton,
)


def test_app_configuration_already_set() -> None:
    """
    Test that App configuration singleton can not be defined if already set
    """
    # Given
    AppConfigurationSingleton._already_set = True  # pylint: disable=protected-access
    config = Mock()

    # When
    error = None
    try:
        AppConfigurationSingleton.define_app_configuration(config)
    except AppConfigurationAlreadySetException as exception:
        error = exception

    # Then
    assert error
    assert str(error) == "app configuration can be set once"
