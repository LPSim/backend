from .emblem_of_severed_fate import EmblemOfSeveredFateArtifacts
from .exile import ExileArtifacts
from .vermillion_shimenawa import VermillionShimenawas
from .heal_by_skill import HealBySkillArtifacts
from .element_artifacts import ElementArtifacts
from .millelith import MillelithArtifacts
from .gamblers import Gamblers
from .instructors_cap import InstructorsCap
from .ocean_hued import OceanHuedArtifacts

from .old_version import OldVersionArtifacts

Artifacts = (
    HealBySkillArtifacts | Gamblers | InstructorsCap | ExileArtifacts
    | EmblemOfSeveredFateArtifacts | MillelithArtifacts | VermillionShimenawas 
    | OceanHuedArtifacts | ElementArtifacts
    # finally old versions
    | OldVersionArtifacts
)
