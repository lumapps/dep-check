from abc import ABC, abstractmethod

from dep_check.models import Dependencies, ModuleWildcard, SourceFile


class IParser(ABC):
    """
    Interface for the code parser
    """

    @abstractmethod
    def wildcard_to_regex(self, module: ModuleWildcard) -> str:
        """
        Return a regex expression for the Module from wildcard
        """

    @abstractmethod
    def find_dependencies(self, source_file: SourceFile) -> Dependencies:
        """
        Find the source files' dependencies
        """

    @abstractmethod
    def find_import_from_dependencies(self, source_file: SourceFile) -> Dependencies:
        """
        Find the source files' from... import" dependencies
        """


def get_dependencies(source_file: SourceFile, parser: IParser) -> Dependencies:
    return parser.find_dependencies(source_file)


def get_import_from_dependencies(
    source_file: SourceFile, parser: IParser
) -> Dependencies:
    return parser.find_import_from_dependencies(source_file)
