#! /usr/bin/env python3
"""
Check dependencies of the project
"""

import argparse
import logging
import sys
from dataclasses import dataclass
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
    "root_dir", type=str, help="The source root dir for search and check."
)
BUILD_PARSER.add_argument(
    "-o",
    "--output",
    type=str,
    help="The name of the yaml file you want",
    default="dependency_config.yaml",
)
BUILD_PARSER.add_argument(
    "--lang",
    type=str,
    help="The language of your project",
    default="python",
    choices=["py", "python", "go", "golang"],
)


CHECK_PARSER = argparse.ArgumentParser(description="Check the dependencies")
CHECK_PARSER.add_argument(
    "check", type=str, help="The check feature.", choices=["check"]
)
CHECK_PARSER.add_argument(
    "root_dir", type=str, help="The source root dir for search and check."
)
CHECK_PARSER.add_argument(
    "-c",
    "--config",
    type=str,
    help="The name of the yaml file you want",
    default="dependency_config.yaml",
)

GRAPH_PARSER = argparse.ArgumentParser(description="Draw a dependency graph")
GRAPH_PARSER.add_argument(
    "graph", type=str, help="The graph feature.", choices=["graph"]
)
GRAPH_PARSER.add_argument(
    "root_dir", type=str, help="The source root dir for search and check."
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
GRAPH_PARSER.add_argument(
    "--lang",
    type=str,
    help="The language of your project",
    choices=["py", "python", "go", "golang"],
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
        source_files = source_file_iterator(self.args.root_dir, self.args.lang[:2])
        return BuildConfigurationUC(
            configuration_io, code_parser, source_files, self.args.lang
        )

    def create_check_use_case(self) -> CheckDependenciesUC:
        """
        Plumbing to make check use case working.
        """
        configuration = YamlConfigurationIO(self.args.config).read()
        code_parser = PythonParser()
        report_printer = ReportPrinter()
        source_files = source_file_iterator(self.args.root_dir, configuration.lang[:2])
        return CheckDependenciesUC(
            configuration, report_printer, code_parser, source_files
        )

    def create_graph_use_case(self) -> DrawGraphUC:
        """
        Plumbing to make draw_graph use case working.
        """
        graph_conf = read_graph_config(self.args.config) if self.args.config else None

        if self.args.lang:
            lang = self.args.lang
        elif graph_conf and "lang" in graph_conf:
            lang = graph_conf["lang"]
        else:
            lang = "python"

        code_parser = PythonParser()
        source_files = source_file_iterator(self.args.root_dir, lang[:2])
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
