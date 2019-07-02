"""
Implementations of IDependenciesPrinter
"""
import logging
from pathlib import Path
from dataclasses import asdict, dataclass
from jinja2 import Template
from subprocess import check_call
from typing import List

import yaml

from dep_check.models import DependencyRules
from dep_check.use_cases.build import IConfigurationWriter
from dep_check.use_cases.check import (
    DependencyError,
    IConfigurationReader,
    IErrorPrinter,
)
from dep_check.use_cases.draw_graph import IGraphDrawer
from dep_check.use_cases.interfaces import Configuration


class YamlConfigurationIO(IConfigurationWriter, IConfigurationReader):
    """
    Configuration yaml serialization.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path

    def write(self, configuration: Configuration) -> None:
        with open(self.config_path, "w") as stream:
            yaml.dump(asdict(configuration), stream)

    def read(self) -> Configuration:
        with open(self.config_path) as stream:
            return Configuration(**yaml.safe_load(stream))


class ErrorLogger(IErrorPrinter):
    """
    Only log errors using logging.error.
    """

    @staticmethod
    def print(errors: List[DependencyError]) -> None:
        """
        Log errors.
        """
        for error in errors:
            logging.error(
                "module %s import %s but is not allowed to (rules: %s)",
                error.module,
                error.dependency,
                error.rules,
            )


@dataclass
class Graph:
    """
    Dataclass representing the informations to draw a graph
    """

    svg_file_name: str
    dot_file_name: str = "/tmp/graph.dot"
    node_color: str = "white"
    background_color: str = "transparent"


class GraphDrawer(IGraphDrawer):
    """
    Write dot / svg files corresponding to the project dependencies
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.header = Template(
            "digraph G {\n"
            "splines=true;\n"
            "node[shape=box fontname=Arial style=filled fillcolor={{nodecolor}}];\n"
            "bgcolor={{bgcolor}}\n\n"
        ).render(nodecolor=self.graph.node_color, bgcolor=self.graph.background_color)
        self.body = ""
        self.footer = "}\n"

    def _write_dot(self, dep_rules: DependencyRules) -> bool:
        if not dep_rules:
            return False

        for module, rules in dep_rules.items():
            for rule in rules:
                self.body += '"{}" -> "{}"\n'.format(module, rule)

        with open(self.graph.dot_file_name, "w") as out:
            out.write(self.header)
            out.write(self.body)
            out.write(self.footer)

        return True

    def _write_svg(self) -> None:
        check_call(
            ["dot", "-Tsvg", self.graph.dot_file_name, "-o", self.graph.svg_file_name]
        )

    def write(self, dep_rules: DependencyRules):
        if Path(self.graph.svg_file_name).suffix == ".dot":
            self.graph.dot_file_name = self.graph.svg_file_name
            self._write_dot(dep_rules)
        else:
            if self._write_dot(dep_rules):
                self._write_svg()
