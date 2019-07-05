from unittest.mock import Mock

from pytest import raises

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

    # When -Then
    with raises(AppConfigurationAlreadySetException):
        AppConfigurationSingleton.define_app_configuration(config)
