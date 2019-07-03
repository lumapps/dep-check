#! /usr/bin/env python3
"""
Check dependencies of the project
"""

import argparse
import sys

from dep_check.infra.file_system import source_file_iterator
from dep_check.infra.io import (
    ErrorLogger,
    Graph,
    GraphDrawer,
    YamlConfigurationIO,
    read_graph_config,
)
from dep_check.infra.std_lib_filter import StdLibSimpleFilter
from dep_check.use_cases.app_configuration import (
    AppConfiguration,
    AppConfigurationSingleton,
)
from dep_check.use_cases.build import BuildConfigurationUC
from dep_check.use_cases.check import CheckDependenciesUC
from dep_check.use_cases.draw_graph import DrawGraphUC
from dep_check.use_cases.interfaces import ExitCode

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
PARSER.add_argument(
    "-g",
    "--graph",
    type=str,
    help="The svg or dot file representing the dependecy graph.",
)
PARSER.add_argument(
    "-o", "--options", type=str, help="The yaml file representing the graph options."
)


class MissingOptionError(Exception):
    """
    DependencyError raised when a missing option is found.
    """


class MainApp:
    """
    Main application class.

    This class is and must be logic-less. Its only aim is to connect
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

        elif self.args.graph:
            graph_uc = self.create_graph_use_case()
            graph_uc.run()

        else:
            raise MissingOptionError("need at least -c, -b or -g option")

        return code.value

    @staticmethod
    def create_app_configuration() -> None:
        """
        Create and set the global application configuration.
        """
        app_configuration = AppConfiguration(std_lib_filter=StdLibSimpleFilter())
        AppConfigurationSingleton.define_app_configuration(app_configuration)

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

    def create_graph_use_case(self) -> DrawGraphUC:
        """
        Plumbing to make draw_graph use case working.
        """
        source_files = source_file_iterator(self.args.root_dir)
        graph_conf = read_graph_config(self.args.options) if self.args.options else None
        graph = Graph(self.args.graph, graph_conf)
        graph_drawer = GraphDrawer(graph)
        return DrawGraphUC(graph_drawer, source_files, graph_conf)


def main() -> None:
    sys.exit(MainApp().main())


if __name__ == "__main__":
    main()
