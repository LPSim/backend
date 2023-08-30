from .element_artifacts import ElementArtifacts
from .others import OtherArtifacts
from .old_version import OldVersionArtifacts

Artifacts = (
    ElementArtifacts | OtherArtifacts
    # finally old versions
    | OldVersionArtifacts
)
