from .others import OtherEventCards
from .arcane_legend import ArcaneLegendCards
from .resonance import NationResonanceCards
from .old_version import OldVersionEventCards


EventCards = (
    OtherEventCards | ArcaneLegendCards | NationResonanceCards
    # finally old version cards
    | OldVersionEventCards
)
