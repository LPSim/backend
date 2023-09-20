from .noelle import Noelle, IGotYourBack
from .arataki_itto import AratakiItto, Ushi, AratakiIchiban
from .stonehide_lawachurl import StonehideLawachurl, StonehideReforged
from .ningguang import Ningguang, StrategicReserve
from .zhongli import Zhongli, StoneStele, DominanceOfEarth


GeoCharactors = (
    Ningguang | Noelle | Zhongli | AratakiItto
    # finally monsters
    | StonehideLawachurl
)
SummonsOfGeoCharactors = StoneStele | Ushi
GeoCharactorTalents = (
    StrategicReserve | IGotYourBack | DominanceOfEarth | AratakiIchiban 
    # finally monsters
    | StonehideReforged
)
