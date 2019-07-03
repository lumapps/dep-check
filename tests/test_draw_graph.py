"""
Test graph use case
"""
from typing import Iterator
from unittest.mock import Mock, patch

from dep_check.infra.io import Graph, GraphDrawer
from dep_check.models import Rule, SourceFile
from dep_check.use_cases.draw_graph import DrawGraphUC

from .fakefile import SIMPLE_FILE


def test_empty_source_files() -> None:
    """
    Test result with no source files given.
    """
    # Given
    source_files: Iterator[SourceFile] = iter([])
    drawer = Mock()
    use_case = DrawGraphUC(drawer, source_files)

    # When
    use_case.run()

    # Then
    drawer.write.assert_called_with({})


def test_nominal(get_source_file_iterator) -> None:
    """
    Test result with a set source files.
    """
    # Given
    source_files = get_source_file_iterator
    drawer = Mock()
    use_case = DrawGraphUC(drawer, source_files)

    # When
    use_case.run()

    # Then
    drawer.write.assert_called()  # type: ignore
    dep_rules = drawer.write.call_args[0][0]
    dependency_rules = {
        module_regex: set(rules) for module_regex, rules in dep_rules.items()
    }

    assert dependency_rules == {
        "simple_module": set(
            (Rule("module"), Rule("module.inside.module"), Rule("amodule"))
        ),
        "amodule.local_module": set(
            (
                Rule("module"),
                Rule("module.inside.module"),
                Rule("amodule"),
                Rule("amodule.inside"),
            )
        ),
        "amodule.std_module": set((Rule("module"), Rule("module.inside.module"))),
    }


def test_dot() -> None:

    # Given
    source_files: Iterator[SourceFile] = iter([SIMPLE_FILE])
    drawer = GraphDrawer(Graph("graph.svg"))
    use_case = DrawGraphUC(drawer, source_files)

    # When
    use_case.run()

    # Then
    with open("/tmp/graph.dot") as dot:
        lines = sorted(dot.readlines())

    assert lines == sorted([
        "digraph G {\n",
        "splines=true;\n",
        "node[shape=box fontname=Arial style=filled fillcolor={}];\n".format(
            drawer.graph.node_color
        ),
        "bgcolor={}\n".format(drawer.graph.background_color),
        '"simple_module" -> "module"\n',
        '"simple_module" -> "module.inside.module"\n',
        '"simple_module" -> "amodule"\n',
        "}\n"
    ])


@patch.object(GraphDrawer, "_write_svg")
def test_not_svg_with_dot(mock_method) -> None:

    # Given
    source_files: Iterator[SourceFile] = iter([SIMPLE_FILE])
    drawer = GraphDrawer(Graph("graph.dot"))
    use_case = DrawGraphUC(drawer, source_files)

    # When
    use_case.run()

    # Then
    mock_method.assert_not_called()
