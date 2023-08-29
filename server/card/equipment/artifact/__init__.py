from .element_artifacts import SmallElementalArtifact
from .old_version import OldVersionArtifacts

Artifacts = (
    SmallElementalArtifact
    # finally old versions
    | OldVersionArtifacts
)
