"""
Implementation of configuration reader and writer
"""
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dep_check.models import Module, SourceCode, SourceFile


def _get_module_from_file_path(path: Path, separator: str) -> Module:
    """
    Transform a filename into a corresponding python module.
    """
    path_without_extention = path.parents[0] / path.stem
    return Module(separator.join(path_without_extention.parts))


@contextmanager
def _change_dir(directory: str) -> Iterator[None]:
    """
    Locally change current working directory
    """
    saved_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(saved_dir)


def _get_python_project_root(root_dir: str) -> str:
    """
    Returns the project root to make sure every module name begins with it
    """
    project_root = ""

    if "__init__.py" in os.listdir(Path(root_dir)):
        project_root = Path(root_dir).name + "."

    for directory in Path(root_dir).parents:
        if "__init__.py" in os.listdir(directory):
            project_root = f"{directory.name}.{project_root}"
        else:
            break
    return project_root


def source_file_iterator(root_dir: str, file_extension: str) -> Iterator[SourceFile]:
    """
    Iterator of all python source files in a directory.
    """
    if file_extension == "py":
        project_root = _get_python_project_root(root_dir)
        separator = "."
    elif file_extension == "go":
        project_root = ""
        separator = "/"

    with _change_dir(root_dir):
        for file_path in Path(".").rglob(f"*.{file_extension}"):
            with open(str(file_path), "r", encoding="utf-8") as stream:
                content = stream.read()
            yield SourceFile(
                Module(project_root + _get_module_from_file_path(file_path, separator)),
                SourceCode(content),
            )
