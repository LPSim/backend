from .noelle import Noelle, IGotYourBack
from .arataki_itto import AratakiItto, Ushi, AratakiIchiban
from .stonehide_lawachurl import StonehideLawachurl, StonehideReforged
from .ningguang import Ningguang, StrategicReserve


GeoCharactors = Noelle | AratakiItto | StonehideLawachurl | Ningguang
SummonsOfGeoCharactors = Ushi | Ushi
GeoCharactorTalents = (
    IGotYourBack | AratakiIchiban | StonehideReforged | StrategicReserve
)
