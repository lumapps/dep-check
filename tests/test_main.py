"""
Test main application.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dep_check.main import DEP_CHECK_FEATURES, MainApp, MissingOptionError
from dep_check.use_cases.app_configuration import AppConfigurationSingleton


@pytest.fixture(autouse=True)
def reset_app_configuration():
    # Given
    AppConfigurationSingleton._already_set = False
    yield
    AppConfigurationSingleton._already_set = False


@patch("dep_check.main.DEP_CHECK_FEATURES", {})
@patch.object(sys, "argv", ["dep_check", "check", "core"])
def test_invalid_feature_raises_missing_option_error() -> None:
    # When / Then
    with pytest.raises(MissingOptionError):
        MainApp()


@patch.object(sys, "argv", ["dep_check", "check", "core"])
def test_valid_check_feature_parses_successfully() -> None:
    # When
    app = MainApp()

    # Then
    assert app.feature == "check"
    assert app.args.modules == [Path("core")]


@patch.object(sys, "argv", ["dep_check", "build", "core"])
def test_valid_build_feature_parses_successfully() -> None:
    # When
    app = MainApp()

    # Then
    assert app.feature == "build"
    assert app.args.modules == [Path("core")]


@patch.object(sys, "argv", ["dep_check", "graph", "core"])
def test_valid_graph_feature_parses_successfully() -> None:
    # When
    app = MainApp()

    # Then
    assert app.feature == "graph"
    assert app.args.modules == [Path("core")]


@patch.object(sys, "argv", ["dep_check", "check", "--config", "test.yaml", "core"])
def test_config_option_before_modules() -> None:
    # When
    app = MainApp()

    # Then
    assert app.feature == "check"
    assert app.args.config == "test.yaml"
    assert app.args.modules == [Path("core")]


@patch.object(sys, "argv", ["dep_check", "check", "core", "--config", "test.yaml"])
def test_config_option_after_modules() -> None:
    # When
    app = MainApp()

    # Then
    assert app.feature == "check"
    assert app.args.config == "test.yaml"
    assert app.args.modules == [Path("core")]


@patch.object(sys, "argv", ["dep_check", "check", "core"])
def test_runtime_keyerror_not_masked() -> None:
    # Given
    app = MainApp()
    mock_use_case = Mock()
    mock_use_case.run.side_effect = KeyError("runtime error")

    with patch.object(
        DEP_CHECK_FEATURES["check"], "use_case_factory", return_value=mock_use_case
    ):
        # When / Then
        with pytest.raises(KeyError, match="runtime error"):
            app.main()
