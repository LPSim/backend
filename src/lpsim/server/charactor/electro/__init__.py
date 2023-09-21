from .fischl import Fischl, Oz, StellarPredator
from .keqing import Keqing, ThunderingPenance, LightningStiletto
from .electro_hypostasis import (
    ElectroHypostasis, AbsorbingPrism, ChainsOfWardingThunder
)
from .raiden_shogun import RaidenShogun, EyeOfStormyJudgment, WishesUnnumbered
from .yae_miko import YaeMiko, TheShrinesSacredShade, SesshouSakura
from .razor import Razor, Awakening
from .beidou import Beidou, LightningStorm
from .kujou_sara import (
    KujouSara, TenguJuuraiAmbush, TenguJuuraiStormcluster, SinOfPride
)
from .cyno import Cyno, FeatherfallJudgment


ElectroCharactors = (
    Fischl | Razor | Keqing | Cyno | Beidou | KujouSara | RaidenShogun 
    | YaeMiko
    # finally monsters
    | ElectroHypostasis
)
SummonsOfElectroCharactors = (
    Oz | TenguJuuraiAmbush | TenguJuuraiStormcluster | EyeOfStormyJudgment 
    | SesshouSakura
    # finally monsters
    | ChainsOfWardingThunder
)
ElectroCharactorTalents = (
    StellarPredator | Awakening | ThunderingPenance | FeatherfallJudgment 
    | LightningStorm | SinOfPride | WishesUnnumbered | TheShrinesSacredShade
    # finally monsters
    | AbsorbingPrism
    # special card for Keqing, treated as a talent card.
    | LightningStiletto
)
