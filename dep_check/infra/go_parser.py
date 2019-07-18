from ctypes import Structure, c_char_p, c_longlong, cdll

from dep_check.dependency_finder import IParser
from dep_check.models import Dependencies, Dependency, SourceFile


class GoString(Structure):  # pylint: disable=too-few-public-methods
    _fields_ = [("data", c_char_p), ("n", c_longlong)]


LIB = cdll.LoadLibrary("dep_check/lib/go_parse.so")
LIB.FindDependencies.argtypes = [GoString]
LIB.FindDependencies.restype = GoString


class GoParser(IParser):
    """
    Implementation of the interface, to parse go
    """

    def find_dependencies(self, source_file: SourceFile) -> Dependencies:
        if source_file.code == "":
            return set()
        deps_string = LIB.FindDependencies(
            GoString(source_file.code.encode(), len(source_file.code))
        )
        deps_list = deps_string.data.decode("utf-8").replace('"', "").split(";")[:-1]

        dependecies: Dependencies = {Dependency(dep) for dep in deps_list}
        return dependecies

    def find_import_from_dependencies(self, source_file: SourceFile) -> Dependencies:
        return self.find_dependencies(source_file)
