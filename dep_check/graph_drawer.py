from subprocess import check_call
from dep_check.models import DependencyRules


def dict_to_dot(
    dep_rules: DependencyRules,
    filename: str = "/tmp/graph.dot",
    node_color: str = "white",
    background_color: str = "transparent",
) -> str:
    if not dep_rules:
        return ""

    with open(filename, "w") as out:
        for line in (
            "digraph G {",
            'size="16,16";',
            "splines=true;",
            "node[shape=box fontname=Arial style=filled fillcolor={}];".format(
                node_color
            ),
            "bgcolor={}".format(background_color),
        ):
            out.write("{}\n".format(line))
        for module, rules in dep_rules.items():
            for rule in rules:
                out.write('"{}" -> "{}"\n'.format(module, rule))
        out.write("}\n")
    return filename


def dot_to_graph(
    dot_filename: str, graph_filename: str = "dependency_graph.svg"
) -> str:
    if dot_filename == "":
        return ""

    check_call(["dot", "-Tsvg", dot_filename, "-o", graph_filename])
    return graph_filename
