import logging
from ctypes import Structure, c_char_p, c_longlong, cdll
from os import environ
from subprocess import CalledProcessError, run

from dep_check.dependency_finder import IParser
from dep_check.models import Dependencies, Dependency, SourceFile


class GoString(Structure):  # pylint: disable=too-few-public-methods
    _fields_ = [("data", c_char_p), ("n", c_longlong)]


class GoParser(IParser):
    """
    Implementation of the interface, to parse go
    """

    def __init__(self):
        self.lib_path = environ.get("GOLIB", f'{environ["HOME"]}/.dep-check')

        try:
            self.lib = cdll.LoadLibrary(f"{self.lib_path}/go_parse.so")
        except OSError:
            logging.info("go_parse.so not found. Building...")
            try:
                run("go get -d github.com/lumapps/dep-check/dep_check/lib", check=True, shell=True)
                run(
                    f"go build -o {self.lib_path}/go_parse.so -buildmode=c-shared "
                    "$GOPATH/src/github.com/lumapps/dep-check/dep_check/lib/go_parse.go",
                    check=True,
                    shell=True
                )
                environ["GOLIB"] = self.lib_path
                logging.info("GO lib go_parse.so built")

            except CalledProcessError:
                logging.error(
                    "Unable to build the GO lib from "
                    "github.com/lumapps/dep-check/dep_check/lib"
                )
                raise

            try:
                self.lib = cdll.LoadLibrary(f"{self.lib_path}/go_parse.so")
                # After building the lib, we try to load it again
            except OSError:
                logging.error("Error while loading the library. Please try again")
                raise

        self.lib.FindDependencies.argtypes = [GoString]
        self.lib.FindDependencies.restype = GoString

    def find_dependencies(self, source_file: SourceFile) -> Dependencies:
        if source_file.code == "":
            return set()
        deps_string = self.lib.FindDependencies(
            GoString(source_file.code.encode(), len(source_file.code))
        )
        deps_list = deps_string.data.decode("utf-8").replace('"', "").split(";")[:-1]

        dependecies: Dependencies = {Dependency(dep) for dep in deps_list}
        return dependecies

    def find_import_from_dependencies(self, source_file: SourceFile) -> Dependencies:
        return self.find_dependencies(source_file)
