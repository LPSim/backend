from .noelle import Noelle, IGotYourBack
from .arataki_itto import AratakiItto
from .stonehide_lawachurl import StonehideLawachurl, StonehideReforged
from .ningguang import Ningguang, StrategicReserve
from .zhongli import Zhongli, StoneStele, DominanceOfEarth
from .albedo import Albedo, SolarIsotoma, DescentOfDivinity


GeoCharactors = (
    Ningguang | Noelle | Zhongli | Albedo | AratakiItto
    # finally monsters
    | StonehideLawachurl
)
SummonsOfGeoCharactors = StoneStele | SolarIsotoma 
GeoCharactorTalents = (
    StrategicReserve | IGotYourBack | DominanceOfEarth | DescentOfDivinity 
    # finally monsters
    | StonehideReforged
)
