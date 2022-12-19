#! /usr/bin/env python3
"""
Check dependencies of the project
"""

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from dep_check.infra.file_system import source_file_iterator
from dep_check.infra.io import (
    Graph,
    GraphDrawer,
    ReportPrinter,
    YamlConfigurationIO,
    read_graph_config,
)
from dep_check.infra.python_parser import PythonParser
from dep_check.infra.std_lib_filter import StdLibSimpleFilter
from dep_check.use_cases.app_configuration import (
    AppConfiguration,
    AppConfigurationSingleton,
)
from dep_check.use_cases.build import BuildConfigurationUC
from dep_check.use_cases.check import CheckDependenciesUC, ForbiddenError
from dep_check.use_cases.draw_graph import DrawGraphUC

FEATURE_PARSER = argparse.ArgumentParser(description="Chose your feature")
FEATURE_PARSER.add_argument(
    "feature",
    type=str,
    help="The feature you want.",
    choices=["build", "check", "graph"],
)

BUILD_PARSER = argparse.ArgumentParser(description="Build your dependency rules")
BUILD_PARSER.add_argument(
    "build", type=str, help="The build feature.", choices=["build"]
)
BUILD_PARSER.add_argument(
    "modules", nargs="+", type=Path, help="The source dirs or files."
)
BUILD_PARSER.add_argument(
    "-o",
    "--output",
    type=str,
    help="The name of the yaml file you want",
    default="dependency_config.yaml",
)


CHECK_PARSER = argparse.ArgumentParser(description="Check the dependencies")
CHECK_PARSER.add_argument(
    "check", type=str, help="The check feature.", choices=["check"]
)
CHECK_PARSER.add_argument(
    "modules", nargs="+", type=Path, help="The source dirs or files."
)
CHECK_PARSER.add_argument(
    "-c",
    "--config",
    type=str,
    help="The name of the yaml file you want",
    default="dependency_config.yaml",
)
CHECK_PARSER.add_argument(
    "--no-unused",
    action="store_true",
    help="Disable unused warning/error.",
)

GRAPH_PARSER = argparse.ArgumentParser(description="Draw a dependency graph")
GRAPH_PARSER.add_argument(
    "graph", type=str, help="The graph feature.", choices=["graph"]
)
GRAPH_PARSER.add_argument(
    "modules", nargs="+", type=Path, help="The source dirs or files."
)
GRAPH_PARSER.add_argument(
    "-o",
    "--output",
    type=str,
    help="The name of the svg/dot file you want",
    default="dependency_graph.svg",
)
GRAPH_PARSER.add_argument(
    "-c", "--config", type=str, help="The yaml file representing the graph options."
)


class MissingOptionError(Exception):
    """
    DependencyError raised when a missing option is found.
    """


@dataclass
class Feature:
    parser: argparse.ArgumentParser
    use_case_factory: Callable


class MainApp:
    """
    Main application class.

    This class is and must be logic-less. Its only aim is to connect
    different components to each other in order to make use_cases working.
    For each abstract interface, this class selects a concrete implementation for the
    application lifetime.
    """

    def __init__(self) -> None:
        self.feature = FEATURE_PARSER.parse_args(sys.argv[1:2]).feature

        try:
            self.args = DEP_CHECK_FEATURES[self.feature].parser.parse_args()
        except KeyError as error:
            raise MissingOptionError() from error

    def main(self) -> None:
        self.create_app_configuration()
        try:
            use_case = DEP_CHECK_FEATURES[self.feature].use_case_factory(self)
            use_case.run()
        except KeyError as error:
            raise MissingOptionError() from error

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
        configuration_io = YamlConfigurationIO(self.args.output)
        code_parser = PythonParser()
        source_files = source_file_iterator(self.args.modules)
        return BuildConfigurationUC(configuration_io, code_parser, source_files)

    def create_check_use_case(self) -> CheckDependenciesUC:
        """
        Plumbing to make check use case working.
        """
        configuration = YamlConfigurationIO(self.args.config).read()
        if self.args.no_unused:
            configuration.check_unused = False
        code_parser = PythonParser()
        report_printer = ReportPrinter(configuration)
        source_files = source_file_iterator(self.args.modules)
        return CheckDependenciesUC(
            configuration, report_printer, code_parser, source_files
        )

    def create_graph_use_case(self) -> DrawGraphUC:
        """
        Plumbing to make draw_graph use case working.
        """
        graph_conf = read_graph_config(self.args.config) if self.args.config else None

        code_parser = PythonParser()
        source_files = source_file_iterator(self.args.modules)
        graph = Graph(self.args.output, graph_conf)
        graph_drawer = GraphDrawer(graph)
        return DrawGraphUC(graph_drawer, code_parser, source_files, graph_conf)


DEP_CHECK_FEATURES = {
    "build": Feature(BUILD_PARSER, MainApp.create_build_use_case),
    "check": Feature(CHECK_PARSER, MainApp.create_check_use_case),
    "graph": Feature(GRAPH_PARSER, MainApp.create_graph_use_case),
}


def main() -> None:
    try:
        MainApp().main()
    except ForbiddenError:
        sys.exit(1)
    except MissingOptionError:
        logging.error(
            "You have to write which feature you want to use among [build,check,graph]"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
