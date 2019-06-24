"""
Implementations of IDependenciesPrinter
"""
import logging
from dataclasses import asdict
from typing import List

import yaml

from use_cases.build import IConfigurationWriter
from use_cases.check import DependencyError, IConfigurationReader, IErrorPrinter
from use_cases.interfaces import Configuration


class YamlConfigurationIO(IConfigurationWriter, IConfigurationReader):
    """
    Configuration yaml serialization.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path

    def write(self, configuration: Configuration) -> None:
        with open(self.config_path, "w") as stream:
            yaml.dump(asdict(configuration), stream)

    def read(self) -> Configuration:
        with open(self.config_path) as stream:
            return Configuration(**yaml.safe_load(stream))


class ErrorLogger(IErrorPrinter):
    """
    Only log errors using logging.error.
    """

    @staticmethod
    def print(errors: List[DependencyError]) -> None:
        """
        Log errors.
        """
        for error in errors:
            logging.error(
                "module %s import %s but is not allowed to (rules: %s)",
                error.module,
                error.dependency,
                error.rules,
            )
