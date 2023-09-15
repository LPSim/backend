from .element_artifacts import ElementArtifacts
from .millelith import MillelithArtifacts
from .gamblers import Gamblers
from .instructors_cap import InstructorsCap

from .old_version import OldVersionArtifacts

Artifacts = (
    InstructorsCap | MillelithArtifacts | Gamblers | ElementArtifacts
    # finally old versions
    | OldVersionArtifacts
)
