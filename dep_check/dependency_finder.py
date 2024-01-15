# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
