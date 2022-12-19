"""
Implementation of configuration reader and writer
"""
import os
from pathlib import Path
from typing import Iterator

from dep_check.models import Module, SourceCode, SourceFile


def _get_python_module(path: Path) -> Module:
    """
    Returns the full module "path" to the given path
    """
    module = []

    if path.is_file():
        module.append(path.stem)

    if path.is_dir() and "__init__.py" in os.listdir(path):
        module.append(path.name)

    for directory in path.parents:
        if "__init__.py" in os.listdir(directory):
            module.append(directory.name)
        else:
            break
    return Module(".".join(reversed(module)))


def _read_file(module_path: Path) -> SourceFile:
    with open(str(module_path), "r", encoding="utf-8") as stream:
        content = stream.read()
    return SourceFile(
        Module(_get_python_module(module_path)),
        SourceCode(content),
    )


def source_file_iterator(modules_path: list[Path]) -> Iterator[SourceFile]:
    """
    Iterator of all python source files in a directory.
    """
    for module_path in modules_path:
        if module_path.is_file():
            yield _read_file(module_path)
            continue
        for submodule_path in module_path.rglob("*.py"):
            yield _read_file(submodule_path)
