from dep_check.models import Module, SourceCode, SourceFile

SIMPLE_FILE = SourceFile(
    module=Module("simple_module"),
    code=SourceCode(
        """
import module
import module.inside.module
from amodule import aclass
"""
    ),
)
FILE_WITH_LOCAL_IMPORT = SourceFile(
    module=Module("amodule.local_module"),
    code=SourceCode(
        """
import module
import module.inside.module
from . import aclass
from .inside import aclass
"""
    ),
)
FILE_WITH_STD_IMPORT = SourceFile(
    module=Module("amodule.std_module"),
    code=SourceCode(
        """
import module
import module.inside.module
import itertools
from abc import ABC
"""
    ),
)

GLOBAL_DEPENDENCIES = {
    "simple_module": set(
        (Module("module"), Module("module.inside.module"), Module("amodule"))
    ),
    "amodule.local_module": set(
        (
            Module("module"),
            Module("module.inside.module"),
            Module("amodule"),
            Module("amodule.inside"),
        )
    ),
    "amodule.std_module": set((Module("module"), Module("module.inside.module"))),
}
