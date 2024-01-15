# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Common use cases interfaces.
"""
import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from dep_check.models import Dependencies, DependencyRules


class UnusedLevel(enum.Enum):
    IGNORE = "ignore"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Configuration:
    """
    The configuration for the tools.
    """

    dependency_rules: DependencyRules = field(default_factory=dict)
    local_init: bool = False
    unused_level: str = UnusedLevel.WARNING.value


class IStdLibFilter(ABC):
    """
    Filter for remove stdlib from dependencies.
    """

    @abstractmethod
    def filter(self, dependencies: Dependencies) -> Dependencies:
        """
        Remove dependencies that are part of stdlib.
        """
