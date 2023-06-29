from enum import Enum


class ElementType(Enum):
    """
    Enum representing the type of an element.

    Attributes:
        FIRE (str): The element is fire.
        WATER (str): The element is water.
        WOOD (str): The element is wood.
        LIGHT (str): The element is light.
        DARK (str): The element is dark.
    """
    CRYO = 'CRYO'
    HYDRO = 'HYDRO'
    PYRO = 'PYRO'
    ELECTRO = 'ELECTRO'
    GEO = 'GEO'
    DENDRO = 'DENDRO'
    ANEMO = 'ANEMO'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


ELEMENT_DEFAULT_ORDER = [
    ElementType.CRYO,
    ElementType.HYDRO,
    ElementType.PYRO,
    ElementType.ELECTRO,
    ElementType.GEO,
    ElementType.DENDRO,
    ElementType.ANEMO,
]


class DiceColor(Enum):
    """
    Enum representing the color of a dice. Besides existing elements, there are
    also Onmi, which can be used as any color.

    Attributes:
        CRYO (str): The dice color is cryo.
        HYDRO (str): The dice color is hydro.
        PYRO (str): The dice color is pyro.
        ELECTRO (str): The dice color is electro.
        GEO (str): The dice color is geo.
        DENDRO (str): The dice color is dendro.
        ANEMO (str): The dice color is anemo.
        OMNI (str): The dice color is omni.
    """
    CRYO = 'CRYO'
    HYDRO = 'HYDRO'
    PYRO = 'PYRO'
    ELECTRO = 'ELECTRO'
    GEO = 'GEO'
    DENDRO = 'DENDRO'
    ANEMO = 'ANEMO'
    OMNI = 'OMNI'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


ELEMENT_TO_DICE_COLOR = {
    ElementType.CRYO: DiceColor.CRYO,
    ElementType.HYDRO: DiceColor.HYDRO,
    ElementType.PYRO: DiceColor.PYRO,
    ElementType.ELECTRO: DiceColor.ELECTRO,
    ElementType.GEO: DiceColor.GEO,
    ElementType.DENDRO: DiceColor.DENDRO,
    ElementType.ANEMO: DiceColor.ANEMO,
}
DICE_COLOR_TO_ELEMENT = {
    DiceColor.CRYO: ElementType.CRYO,
    DiceColor.HYDRO: ElementType.HYDRO,
    DiceColor.PYRO: ElementType.PYRO,
    DiceColor.ELECTRO: ElementType.ELECTRO,
    DiceColor.GEO: ElementType.GEO,
    DiceColor.DENDRO: ElementType.DENDRO,
    DiceColor.ANEMO: ElementType.ANEMO,
}
