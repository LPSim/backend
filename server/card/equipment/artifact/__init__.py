from .element_artifacts import ElementArtifacts
from .millelith import MillelithArtifacts
from .gamblers import Gamblers

from .old_version import OldVersionArtifacts

Artifacts = (
    MillelithArtifacts | Gamblers | ElementArtifacts
    # finally old versions
    | OldVersionArtifacts
)
