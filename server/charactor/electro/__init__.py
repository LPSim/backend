from .fischl import Fischl, Oz, StellarPredator
from .keqing import Keqing, ThunderingPenance, LightningStiletto
from .electro_hypostasis import (
    ElectroHypostasis, AbsorbingPrism, ChainsOfWardingThunder
)


ElectroCharactors = Fischl | Keqing | ElectroHypostasis
SummonsOfElectroCharactors = Oz | ChainsOfWardingThunder
ElectroCharactorTalents = (
    StellarPredator | ThunderingPenance | AbsorbingPrism
    # special card for Keqing, treated as a talent card.
    | LightningStiletto
)
