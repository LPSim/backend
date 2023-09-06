from .fischl import Fischl, Oz, StellarPredator
from .keqing import Keqing, ThunderingPenance, LightningStiletto


ElectroCharactors = Fischl | Keqing
SummonsOfElectroCharactors = Oz | Oz
ElectroCharactorTalents = (
    StellarPredator | ThunderingPenance 
    # special card for Keqing, treated as a talent card.
    | LightningStiletto
)
