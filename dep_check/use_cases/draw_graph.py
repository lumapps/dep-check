"""
Draws a graph of the dependencies between modules
"""
from dep_check.graph_drawer import dict_to_dot, dot_to_graph

from .check import IConfigurationReader


class DrawGraphUC:
    def __init__(
        self,
        configuration_reader: IConfigurationReader,
        node_color: str,
        bgcolor: str,
        graph_name: str,
    ):
        self.configuration = configuration_reader.read()
        self.node_color = node_color
        self.bgcolor = bgcolor
        self.graph_name = graph_name

    def run(self) -> None:
        dot_file = dict_to_dot(
            self.configuration.dependency_rules,
            node_color=self.node_color,
            background_color=self.bgcolor,
        )
        dot_to_graph(dot_file, self.graph_name)
