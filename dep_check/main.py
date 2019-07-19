#! /usr/bin/env python3
"""
Check dependencies of the project
"""

import argparse
import logging
import sys

from dep_check.infra.file_system import source_file_iterator
from dep_check.infra.go_parser import GoParser
from dep_check.infra.io import (
    ErrorLogger,
    Graph,
    GraphDrawer,
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
from dep_check.use_cases.check import CheckDependenciesUC
from dep_check.use_cases.draw_graph import DrawGraphUC
from dep_check.use_cases.interfaces import ExitCode

BUILD_PARSER = argparse.ArgumentParser(description="Build your dependency rules")
BUILD_PARSER.add_argument(
    "build", type=str, help="The build feature.", choices=["build"]
)
BUILD_PARSER.add_argument(
    "root_dir", type=str, help="The source root dir for search and check."
)
BUILD_PARSER.add_argument(
    "-o", "--output", type=str, help="The name of the yaml file you want"
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
    "-c", "--config", type=str, help="The name of the yaml file you want"
)


GRAPH_PARSER = argparse.ArgumentParser(description="Draw a dependency graph")
GRAPH_PARSER.add_argument(
    "graph", type=str, help="The graph feature.", choices=["graph"]
)
GRAPH_PARSER.add_argument(
    "root_dir", type=str, help="The source root dir for search and check."
)
GRAPH_PARSER.add_argument(
    "-o", "--output", type=str, help="The name of the svg/dot file you want"
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


class MainApp:
    """
    Main application class.

    This class is and must be logic-less. Its only aim is to connect
    different components to each other in order to make use_cases working.
    For each abstract interface, this class selects a concrete implementation for the
    application lifetime.
    """

    def __init__(self) -> None:
        try:
            self.feature = sys.argv[1]
        except IndexError:
            logging.error(
                "You have to write which feature you want to use among [build,check,graph]"
            )
            raise
        if self.feature == "build":
            self.args = BUILD_PARSER.parse_args()
            self.file_name = (
                self.args.output if self.args.output else "dependency_config.yaml"
            )
        elif self.feature == "check":
            self.args = CHECK_PARSER.parse_args()
            self.file_name = (
                self.args.config if self.args.config else "dependency_config.yaml"
            )
        elif self.feature == "graph":
            self.args = GRAPH_PARSER.parse_args()
            self.file_name = (
                self.args.output if self.args.output else "dependency_graph.svg"
            )

    def main(self) -> int:
        code = ExitCode.OK
        self.create_app_configuration()

        if self.feature == "build":
            build_uc = self.create_build_use_case()
            build_uc.run()

        elif self.feature == "check":
            check_uc = self.create_check_use_case()
            code = check_uc.run()

        elif self.feature == "graph":
            graph_uc = self.create_graph_use_case()
            graph_uc.run()

        else:
            raise MissingOptionError(
                "You have to write which feature you want to use among [build,check,graph]"
            )

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
        configuration_io = YamlConfigurationIO(self.file_name)
        code_parser = (
            PythonParser() if self.args.lang in ["py", "python"] else GoParser()
        )
        source_files = source_file_iterator(self.args.root_dir, self.args.lang[:2])
        return BuildConfigurationUC(
            configuration_io, code_parser, source_files, self.args.lang
        )

    def create_check_use_case(self) -> CheckDependenciesUC:
        """
        Plumbing to make check use case working.
        """
        configuration = YamlConfigurationIO(self.file_name).read()
        code_parser = (
            PythonParser() if configuration.lang in ["py", "python"] else GoParser()
        )
        error_printer = ErrorLogger()
        source_files = source_file_iterator(self.args.root_dir, configuration.lang[:2])
        return CheckDependenciesUC(
            configuration, error_printer, code_parser, source_files
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

        code_parser = PythonParser() if lang in ["py", "python"] else GoParser()
        source_files = source_file_iterator(self.args.root_dir, lang[:2])
        graph = Graph(self.file_name, graph_conf)
        graph_drawer = GraphDrawer(graph)
        return DrawGraphUC(graph_drawer, code_parser, source_files, graph_conf)


def main() -> None:
    sys.exit(MainApp().main())


if __name__ == "__main__":
    main()
