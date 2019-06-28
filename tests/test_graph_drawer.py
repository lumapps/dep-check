"""
Test graph use case
"""

from dep_check.models import Rule
from dep_check.graph_drawer import dict_to_dot, dot_to_graph


_SIMPLE_DICT = {
    "simple_module": [Rule("module%"), Rule("amodule")],
    "amodule.*": [Rule("module"), Rule("module.inside.*"), Rule("amodule%")],
}


def test_dict_empty() -> None:
    """
    Test result with an empty dictionary.
    """
    # Given
    empty_dict = {}
    # When
    dot_file = dict_to_dot(empty_dict)

    # Then
    assert dot_file == ""

def test_dot_file_name_empty() -> None:
    """
    Test result with an empty dot file name.
    """
    # Given
    dot_filename = ""
    # When
    svg_file = dot_to_graph(dot_filename)

    # Then
    assert svg_file == ""

def test_simple_dict() -> None:
    """
    Test result with a simple dictionary
    """
    # Given

    # When
    dot_file = dict_to_dot(_SIMPLE_DICT)

    # Then
    with open(dot_file, 'r') as file:
        dot = file.readlines()

    assert dot == [
            "digraph G {\n",
            'size="16,16";\n',
            "splines=true;\n",
            "node[shape=box fontname=Arial style=filled fillcolor=white];\n",
            "bgcolor=transparent\n",
            '"simple_module" -> "module%"\n',
            '"simple_module" -> "amodule"\n',
            '"amodule.*" -> "module"\n',
            '"amodule.*" -> "module.inside.*"\n',
            '"amodule.*" -> "amodule%"\n',
            '}\n'
    ]
