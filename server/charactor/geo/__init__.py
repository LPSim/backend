from .noelle import Noelle, IGotYourBack
from .arataki_itto import AratakiItto, Ushi, AratakiIchiban
from .stonehide_lawachurl import StonehideLawachurl, StonehideReforged
from .ningguang import Ningguang, StrategicReserve


GeoCharactors = (
    Ningguang | Noelle | AratakiItto
    # finally monsters
    | StonehideLawachurl
)
SummonsOfGeoCharactors = Ushi | Ushi
GeoCharactorTalents = (
    StrategicReserve | IGotYourBack | AratakiIchiban 
    # finally monsters
    | StonehideReforged
)
