from dep_check.models import Dependency, Module, SourceCode, SourceFile

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
        (
            Dependency(Module("module")),
            Dependency(Module("module.inside.module")),
            Dependency(Module("amodule")),
        )
    ),
    "amodule.local_module": set(
        (
            Dependency(Module("module")),
            Dependency(Module("module.inside.module")),
            Dependency(Module("amodule")),
            Dependency(Module("amodule.inside")),
        )
    ),
    "amodule.std_module": set(
        (Dependency(Module("module")), Dependency(Module("module.inside.module")))
    ),
}
