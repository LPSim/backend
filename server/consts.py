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


class DieColor(Enum):
    """
    Enum representing the color of a die. It can also be called as elemental
    type, elemental attributes. Besides existing element types, there are
    also Onmi, which can be used as any color.

    Attributes:
        CRYO (str): The die color is cryo.
        HYDRO (str): The die color is hydro.
        PYRO (str): The die color is pyro.
        ELECTRO (str): The die color is electro.
        GEO (str): The die color is geo.
        DENDRO (str): The die color is dendro.
        ANEMO (str): The die color is anemo.
        OMNI (str): The die color is omni.
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


ELEMENT_TO_DIE_COLOR = {
    ElementType.CRYO: DieColor.CRYO,
    ElementType.HYDRO: DieColor.HYDRO,
    ElementType.PYRO: DieColor.PYRO,
    ElementType.ELECTRO: DieColor.ELECTRO,
    ElementType.GEO: DieColor.GEO,
    ElementType.DENDRO: DieColor.DENDRO,
    ElementType.ANEMO: DieColor.ANEMO,
}
DIE_COLOR_TO_ELEMENT = {
    DieColor.CRYO: ElementType.CRYO,
    DieColor.HYDRO: ElementType.HYDRO,
    DieColor.PYRO: ElementType.PYRO,
    DieColor.ELECTRO: ElementType.ELECTRO,
    DieColor.GEO: ElementType.GEO,
    DieColor.DENDRO: ElementType.DENDRO,
    DieColor.ANEMO: ElementType.ANEMO,
}
