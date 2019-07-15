"""
Implementations of IDependenciesPrinter
"""
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from subprocess import check_call
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import yaml
from jinja2 import Template

from dep_check.models import GlobalDependencies, Module, Rules, iter_all_modules
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
            stream.write("---\n\n")
            yaml.safe_dump(asdict(configuration), stream)

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

    @staticmethod
    def warn(unused_rules: Rules) -> None:
        """
        Log warnings
        """
        for module, rule in unused_rules:
            logging.warning("rule not used  %s: %s", module, rule)


def read_graph_config(conf_path: str) -> Dict:
    """
    Used to read the graph configuration file, and make it a Dictionary
    """
    with open(conf_path) as stream:
        return yaml.safe_load(stream)


@dataclass(init=False)
class Graph:
    """
    Dataclass representing the information to draw a graph
    """

    def __init__(self, svg_file_name: str, graph_config: Optional[Dict] = None):
        self.svg_file_name = svg_file_name
        self.graph_config = graph_config or {}
        self.dot_file_name: str = "/tmp/graph.dot"
        self.node_color: str = self.graph_config.get("node_color", "white")
        self.background_color: str = self.graph_config.get("bgcolor", "transparent")
        self.layers: dict = self.graph_config.get("layers", {})


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
            "bgcolor={{bgcolor}}\n\n\n"
        ).render(nodecolor=self.graph.node_color, bgcolor=self.graph.background_color)
        self.body = ""
        self.footer = "}\n"

        self.subgraph = Template(
            "subgraph cluster_{{subgraph_name}} {\n"
            "node [style=filled fillcolor={{color}}];\n"
            "{{list_modules}};\n"
            'label="{{subgraph_name}}";\n'
            "color={{color}};\n"
            "penwidth=2;\n"
            "}\n\n\n"
        )

    def _iter_layer_modules(
        self, global_dep: GlobalDependencies
    ) -> Iterator[Tuple[str, Iterable[Module]]]:

        for layer in self.graph.layers:
            yield layer, [
                m
                for m in iter_all_modules(global_dep)
                if m.startswith(tuple(self.graph.layers[layer]["modules"]))
            ]

    def _write_dot(self, global_dep: GlobalDependencies) -> bool:
        if not global_dep:
            return False

        for layer, modules in self._iter_layer_modules(global_dep):

            self.body += self.subgraph.render(
                subgraph_name=layer,
                color=self.graph.layers[layer].get("color", self.graph.node_color),
                list_modules=str(modules)[1:-1].replace("'", '"'),
            )

        for module, deps in global_dep.items():
            for dep in deps:
                self.body += '"{}" -> "{}"\n'.format(module, dep.main_import)

        with open(self.graph.dot_file_name, "w") as out:
            out.write(self.header)
            out.write(self.body)
            out.write(self.footer)

        return True

    def _write_svg(self) -> None:
        check_call(
            ["dot", "-Tsvg", self.graph.dot_file_name, "-o", self.graph.svg_file_name]
        )

    def write(self, global_dep: GlobalDependencies):
        if Path(self.graph.svg_file_name).suffix == ".dot":
            self.graph.dot_file_name = self.graph.svg_file_name
            self._write_dot(global_dep)
        else:
            if self._write_dot(global_dep):
                self._write_svg()
