from .noelle import Noelle, IGotYourBack
from .arataki_itto import AratakiItto, Ushi, AratakiIchiban
from .stonehide_lawachurl import StonehideLawachurl, StonehideReforged
from .ningguang import Ningguang, StrategicReserve
from .zhongli import Zhongli, StoneStele, DominanceOfEarth
from .albedo import Albedo, SolarIsotoma, DescentOfDivinity


GeoCharactors = (
    Ningguang | Noelle | Zhongli | Albedo | AratakiItto
    # finally monsters
    | StonehideLawachurl
)
SummonsOfGeoCharactors = StoneStele | SolarIsotoma | Ushi
GeoCharactorTalents = (
    StrategicReserve | IGotYourBack | DominanceOfEarth | DescentOfDivinity 
    | AratakiIchiban 
    # finally monsters
    | StonehideReforged
)
