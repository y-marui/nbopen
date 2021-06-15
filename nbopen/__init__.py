"""Open a notebook from the command line in the best available server"""

__version__ = '0.6'

from traitlets.config.configurable import Configurable
from traitlets.config.loader import PyFileConfigLoader
from pathlib import Path
from traitlets.config import Config

lib_name = "nbopen"
rep_name = lib_name.lower()


def get_configdir(create=False) -> Path:
    """Return path of the the configuration directory: CONFIGDIR.

    The directory is chosen as follows:

    1. ``$HOME/.config/{rep_name}``
    2. ``$HOME/.{rep_name}``
    """

    def gen_candidates():
        yield Path.home() / ".config" / rep_name
        yield Path.home() / f".{rep_name}"

    for path in gen_candidates():
        if path.exists() and path.is_dir():
            return path

    for path in gen_candidates():
        if path.parent.exists() and path.parent.is_dir():
            if create:
                path.mkdir(parents=True, exist_ok=True)
            return path


def fname():
    """Return path of the the config file.

    The file location is chosen as follows

    1. ``$(pwd)/{rep_name}rc.py``
    2. ``$CONFIGDIR/config.py``
        ``$CONFIGDIR`` is determined by ``get_configdir``
    3. ``$HOME/.{rep_name}rc.py``
    4. ``$HOME/.config/{rep_name}rc.py``
    """

    def gen_candidates():
        yield Path.cwd() / f"{rep_name}rc.py"
        yield get_configdir() / "config.py"
        yield Path.home() / f".{rep_name}rc.py"
        yield Path.home() / ".config" / f"{rep_name}rc.py"

    for cand in gen_candidates():
        if cand.exists() and not cand.is_dir():
            return cand


def load_config():
    """Load config."""
    p = Path(__file__).with_name("config.py")
    PyFileConfigLoader(str(p)).load_config()

    p = fname()
    if p:
        PyFileConfigLoader(str(p)).load_config()


# define c before load_config()
c = Configurable.config = Config()
load_config()

if c:
    # load main after load config
    from .nbopen import main
