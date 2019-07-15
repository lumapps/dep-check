import ast
from typing import Any, FrozenSet, List

from dep_check.models import Dependencies, Dependency, Module, SourceFile


class _ImportVisitor(ast.NodeVisitor):
    """
    Implementation of a NodeVisitor, to scan import of a python code.
    """

    def __init__(self, current_module: str) -> None:
        self._dependencies: Dependencies = set()
        self.current_module_parts: List[str] = current_module.split(".")

    @property
    def dependencies(self) -> Dependencies:
        """
        Dependencies found during the scan.
        """
        return self._dependencies

    def visit(self, node: Any) -> None:
        modules: FrozenSet[Dependency] = frozenset()
        if isinstance(node, ast.Import):
            modules = frozenset(Dependency(Module(alias.name)) for alias in node.names)

        elif isinstance(node, ast.ImportFrom):
            module = Module(node.module or "")
            if node.level:
                parent_module = ".".join(self.current_module_parts[: -node.level])
                if node.module:
                    module = Module("{}.{}".format(parent_module, node.module))
                else:
                    module = Module(parent_module)
            modules = frozenset((Dependency(module),))
        self._dependencies |= modules

        super().visit(node)


class _ImportFromVisitor(ast.NodeVisitor):
    def __init__(self, current_module: str) -> None:
        self._dependencies: Dependencies = set()
        self.current_module_parts: List[str] = current_module.split(".")

    @property
    def dependencies(self) -> Dependencies:
        """
        Dependencies found during the scan.
        """
        return self._dependencies

    def visit(self, node: Any) -> None:
        modules: FrozenSet[Dependency] = frozenset()
        if isinstance(node, ast.Import):
            modules = frozenset(Dependency(Module(alias.name)) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = Module(node.module or "")
            if node.level:
                parent_module = ".".join(self.current_module_parts[: -node.level])
                if node.module:
                    module = Module("{}.{}".format(parent_module, node.module))
                else:
                    module = Module(parent_module)
            sub_imports = frozenset(Module(alias.name) for alias in node.names)
            modules = frozenset((Dependency(module, sub_imports),))

        self._dependencies |= modules

        super().visit(node)


def find_dependencies(source_file: SourceFile) -> Dependencies:
    """
    Scan a python source file and return its dependencies.
    """
    visitor = _ImportVisitor(source_file.module)
    node = ast.parse(source_file.code)
    visitor.visit(node)
    return visitor.dependencies


def find_import_from_dependencies(source_file: SourceFile) -> Dependencies:
    """
    Scan a python source file and return its dependencies.
    """
    visitor = _ImportFromVisitor(source_file.module)
    node = ast.parse(source_file.code)
    visitor.visit(node)
    return visitor.dependencies
