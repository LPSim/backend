from .fischl import Fischl, Oz, StellarPredator
from .keqing import Keqing, ThunderingPenance, LightningStiletto
from .electro_hypostasis import (
    ElectroHypostasis, AbsorbingPrism, ChainsOfWardingThunder
)
from .raiden_shogun import RaidenShogun, EyeOfStormyJudgment, WishesUnnumbered
from .yaemiko import YaeMiko, TheShrinesSacredShade, SesshouSakura


ElectroCharactors = (
    Fischl | Keqing | ElectroHypostasis | RaidenShogun | YaeMiko
)
SummonsOfElectroCharactors = (
    Oz | ChainsOfWardingThunder | EyeOfStormyJudgment | SesshouSakura
)
ElectroCharactorTalents = (
    StellarPredator | ThunderingPenance | AbsorbingPrism | WishesUnnumbered
    | TheShrinesSacredShade
    # special card for Keqing, treated as a talent card.
    | LightningStiletto
)
