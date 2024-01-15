# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Application global configuration.
"""
from dataclasses import dataclass

from .interfaces import IStdLibFilter


class AppConfigurationAlreadySetException(Exception):
    """
    Exception when you try to set app configuration twice.
    """


@dataclass(frozen=True)
class AppConfiguration:
    """
    Configuration define at application level (in general in main).
    """

    std_lib_filter: IStdLibFilter


class AppConfigurationSingleton:
    """
    App configuration singleton
    """

    _instance: AppConfiguration
    _already_set: bool = False

    @classmethod
    def define_app_configuration(cls, configuration: AppConfiguration) -> None:
        """
        Define the application configuration to use during this run.
        Can only be called once.
        """
        if cls._already_set:
            raise AppConfigurationAlreadySetException(
                "app configuration can be set once"
            )
        cls._instance = configuration
        cls._already_set = True

    @classmethod
    def get_instance(cls) -> AppConfiguration:
        """
        Get current app configuration instance.
        raise if not define.
        """
        return cls._instance
