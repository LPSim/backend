from .lucky_dog import LuckyDogsSilverCirclet
from .element_artifacts import ElementArtifacts
from .millelith import MillelithArtifacts
from .gamblers import Gamblers
from .instructors_cap import InstructorsCap

from .old_version import OldVersionArtifacts

Artifacts = (
    LuckyDogsSilverCirclet | Gamblers | InstructorsCap | MillelithArtifacts 
    | ElementArtifacts
    # finally old versions
    | OldVersionArtifacts
)
