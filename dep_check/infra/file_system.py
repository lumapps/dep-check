"""
Implementation of configuration reader and writer
"""

import inspect
from pathlib import Path
from typing import Iterator

from dep_check.models import Module, SourceCode, SourceFile


def _get_python_module(path: Path) -> Module:
    """
    Returns the full module "path" to the given path
    """
    name = None
    if path.is_file():
        name = inspect.getmodulename(str(path))
    elif path.is_dir():
        name = path.name
    if not name:
        raise ModuleNotFoundError("Cannot find module name", path=str(path))

    full_path = list(p.name for p in path.parents[:-1])
    full_path.reverse()
    full_path.append(name)

    module = ".".join(full_path)

    return Module(module)


def _read_file(module_path: Path) -> SourceFile:
    with open(str(module_path), "r", encoding="utf-8") as stream:
        content = stream.read()
    return SourceFile(
        Module(_get_python_module(module_path)),
        SourceCode(content),
    )


def source_file_iterator(
    files_path: list[Path], root_path: Path
) -> Iterator[SourceFile]:
    """
    Iterator of all python source files in a directory.
    """
    for file_path in files_path:
        module_path = file_path.absolute().relative_to(root_path)
        if module_path.is_file():
            yield _read_file(module_path)
            continue
        for submodule_path in module_path.rglob("*.py"):
            yield _read_file(submodule_path)
