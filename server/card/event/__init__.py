from .others import OtherEventCards
from .arcane_legend import ArcaneLegendCards
from .resonance import NationResonanceCards


EventCards = OtherEventCards | ArcaneLegendCards | NationResonanceCards
