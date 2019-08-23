import logging
from os import chdir
from subprocess import CalledProcessError, run

from dep_check.dependency_finder import IParser
from dep_check.models import Dependencies, Dependency, ModuleWildcard, SourceFile

try:
    from dep_check.lib import goparse
except ImportError:
    chdir("dep_check/lib")
    try:
        run(["go", "build", "-buildmode=c-shared", "-o", "goparse.so"], check=True)
        from dep_check.lib import goparse  # pylint: disable=no-name-in-module
    except (CalledProcessError, FileNotFoundError):
        logging.warning(
            "Couldn't load GO library, you won't be able to use dep-check on GO projects."
        )
    except ImportError:
        logging.warning(
            "Couldn't importy GO library, you won't be able to use dep-check on GO projects."
        )
    chdir("../..")


class GoParser(IParser):
    """
    Implementation of the interface, to parse go
    """

    def wildcard_to_regex(self, module: ModuleWildcard) -> str:
        """
        Return a regex expression for the Module from wildcard
        """
        module_regex = module.replace(".", "\\.").replace("*", ".*")
        module_regex = module_regex.replace("[!", "[^").replace("?", ".?")

        # Special char including a module along with all its sub-modules:
        module_regex = module_regex.replace("%", r"(/.*)?$")
        return module_regex

    def find_dependencies(self, source_file: SourceFile) -> Dependencies:
        if not source_file.code:
            return set()
        deps_string = goparse.find_dependencies(source_file.code)
        deps_list = deps_string.replace('"', "").split(";")[:-1]

        dependecies: Dependencies = {Dependency(dep) for dep in deps_list}
        return dependecies

    def find_import_from_dependencies(self, source_file: SourceFile) -> Dependencies:
        return self.find_dependencies(source_file)
