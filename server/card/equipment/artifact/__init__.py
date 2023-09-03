from .element_artifacts import ElementArtifacts
from .millelith import MillelithArtifacts
from .others import OtherArtifacts

from .old_version import OldVersionArtifacts

Artifacts = (
    ElementArtifacts | MillelithArtifacts | OtherArtifacts
    # finally old versions
    | OldVersionArtifacts
)
