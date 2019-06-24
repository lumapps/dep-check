#! /usr/bin/env python3
"""
Check dependencies of the project
"""

import argparse
import sys

from infra.file_system import source_file_iterator
from infra.io import ErrorLogger, YamlConfigurationIO
from infra.std_lib_filter import StdLibSimpleFilter
from use_cases.app_configuration import AppConfiguration, AppConfigurationSingelton
from use_cases.build import BuildConfigurationUC
from use_cases.check import CheckDependenciesUC
from use_cases.interfaces import ExitCode

PARSER = argparse.ArgumentParser(
    description="Small program that ensure dependency rules are respected"
)
PARSER.add_argument(
    "root_dir", type=str, help="The source root dir for search and check."
)
PARSER.add_argument(
    "-c",
    "--config",
    type=str,
    help="The file describing configuration and dependency rules (white list).",
)
PARSER.add_argument(
    "-b", "--build", type=str, help="Build configuration file with existing code."
)


class MissingOptionError(Exception):
    """
    DependencyError raised when a missing option is found.
    """


class MainApp:
    """
    Main application class.

    This class is and must be logicless. Its only aim is to connect
    different components to each other in order to make use_cases working.
    For each abstract interface, this class selects a concrete implementation for the
    application lifetime.
    """

    def __init__(self) -> None:
        self.args = PARSER.parse_args()

    def main(self) -> int:
        code = ExitCode.OK
        self.create_app_configuration()
        if self.args.build:
            build_uc = self.create_build_use_case()
            build_uc.run()

        elif self.args.config:
            check_uc = self.create_check_use_case()
            code = check_uc.run()

        else:
            raise MissingOptionError("need at least -c or -b option")

        return code.value

    @staticmethod
    def create_app_configuration() -> None:
        """
        Create and set the global application configuration.
        """
        app_configuration = AppConfiguration(std_lib_filter=StdLibSimpleFilter())
        AppConfigurationSingelton.define_app_configuration(app_configuration)

    def create_build_use_case(self) -> BuildConfigurationUC:
        """
        Plumbing to make build use case working.
        """
        configuration_io = YamlConfigurationIO(self.args.build)
        source_files = source_file_iterator(self.args.root_dir)
        return BuildConfigurationUC(configuration_io, source_files)

    def create_check_use_case(self) -> CheckDependenciesUC:
        """
        Plumbing to make check use case working.
        """
        configuration_reader = YamlConfigurationIO(self.args.config)
        error_printer = ErrorLogger()
        source_files = source_file_iterator(self.args.root_dir)
        return CheckDependenciesUC(configuration_reader, error_printer, source_files)

def main() -> None:
    sys.exit(MainApp().main())

if __name__ == "__main__":
    main()

