from .fischl import Fischl, Oz, StellarPredator
from .keqing import Keqing, ThunderingPenance, LightningStiletto
from .electro_hypostasis import (
    ElectroHypostasis, AbsorbingPrism, ChainsOfWardingThunder
)
from .raiden_shogun import RaidenShogun, EyeOfStormyJudgment, WishesUnnumbered


ElectroCharactors = Fischl | Keqing | ElectroHypostasis | RaidenShogun
SummonsOfElectroCharactors = Oz | ChainsOfWardingThunder | EyeOfStormyJudgment
ElectroCharactorTalents = (
    StellarPredator | ThunderingPenance | AbsorbingPrism | WishesUnnumbered
    # special card for Keqing, treated as a talent card.
    | LightningStiletto
)
