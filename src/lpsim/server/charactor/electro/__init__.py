from .fischl import Fischl, Oz, StellarPredator
from .keqing import Keqing, ThunderingPenance, LightningStiletto
from .electro_hypostasis import (
    ElectroHypostasis, AbsorbingPrism, ChainsOfWardingThunder
)
from .raiden_shogun import RaidenShogun, EyeOfStormyJudgment, WishesUnnumbered
from .yae_miko import YaeMiko, TheShrinesSacredShade, SesshouSakura
from .razor import Razor, Awakening


ElectroCharactors = (
    Fischl | Razor | Keqing | RaidenShogun | YaeMiko
    # finally monsters
    | ElectroHypostasis
)
SummonsOfElectroCharactors = (
    Oz | EyeOfStormyJudgment | SesshouSakura
    # finally monsters
    | ChainsOfWardingThunder
)
ElectroCharactorTalents = (
    StellarPredator | Awakening | ThunderingPenance | WishesUnnumbered
    | TheShrinesSacredShade
    # finally monsters
    | AbsorbingPrism
    # special card for Keqing, treated as a talent card.
    | LightningStiletto
)
