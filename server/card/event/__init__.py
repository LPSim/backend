from .others import OtherEventCards
from .arcane_legend import ArcaneLegendCards
from .resonance import ElementResonanceCards, NationResonanceCards
from .foods import FoodCards
from .old_version import OldVersionEventCards


EventCards = (
    OtherEventCards | ArcaneLegendCards | ElementResonanceCards 
    | NationResonanceCards | FoodCards
    # finally old version cards
    | OldVersionEventCards
)
