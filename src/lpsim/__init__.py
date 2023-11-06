from .server.deck import Deck  # noqa: F401
from .server.match import Match, MatchState  # noqa: F401


try:
    from ._version import __version__, __version_tuple__  # type: ignore
except ModuleNotFoundError:
    __version__ = 'unknown'
    __version_tuple__ = (0, 0, 0)
