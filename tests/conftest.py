import pytest
from dep_check.use_cases.app_configuration import AppConfiguration, AppConfigurationSingleton
from dep_check.infra.std_lib_filter import StdLibSimpleFilter
from dep_check.models import SourceFile
from typing import Iterator
from .fakefile import SIMPLE_FILE, FILE_WITH_LOCAL_IMPORT, FILE_WITH_STD_IMPORT

@pytest.fixture(scope="session", autouse="true")
def setup_application_config() -> None:
    """
    Define application configuration.
    """
    app_configuration = AppConfiguration(std_lib_filter=StdLibSimpleFilter())
    AppConfigurationSingleton.define_app_configuration(app_configuration)



@pytest.fixture(scope="session")
def get_source_file_iterator() -> Iterator[SourceFile]:
    """
    Iter over test source files.
    """
    yield SIMPLE_FILE, FILE_WITH_LOCAL_IMPORT, FILE_WITH_STD_IMPORT
