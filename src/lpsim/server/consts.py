from enum import Enum


class ElementType(str, Enum):
    """
    Enum representing the type of an element.
    """
    NONE = 'NONE'
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


class DieColor(str, Enum):
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


class DamageElementalType(str, Enum):
    """
    Enum representing the type of a damage.
    """
    # elemental damage
    CRYO = 'CRYO'
    HYDRO = 'HYDRO'
    PYRO = 'PYRO'
    ELECTRO = 'ELECTRO'
    GEO = 'GEO'
    DENDRO = 'DENDRO'
    ANEMO = 'ANEMO'

    # other damage
    PHYSICAL = 'PHYSICAL'
    PIERCING = 'PIERCING'
    HEAL = 'HEAL'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


ELEMENT_TO_DAMAGE_TYPE = {
    ElementType.NONE: DamageElementalType.PHYSICAL,
    ElementType.CRYO: DamageElementalType.CRYO,
    ElementType.HYDRO: DamageElementalType.HYDRO,
    ElementType.PYRO: DamageElementalType.PYRO,
    ElementType.ELECTRO: DamageElementalType.ELECTRO,
    ElementType.GEO: DamageElementalType.GEO,
    ElementType.DENDRO: DamageElementalType.DENDRO,
    ElementType.ANEMO: DamageElementalType.ANEMO,
}
DAMAGE_TYPE_TO_ELEMENT = {
    DamageElementalType.CRYO: ElementType.CRYO,
    DamageElementalType.HYDRO: ElementType.HYDRO,
    DamageElementalType.PYRO: ElementType.PYRO,
    DamageElementalType.ELECTRO: ElementType.ELECTRO,
    DamageElementalType.GEO: ElementType.GEO,
    DamageElementalType.DENDRO: ElementType.DENDRO,
    DamageElementalType.ANEMO: ElementType.ANEMO,
    DamageElementalType.PHYSICAL: ElementType.NONE,
    DamageElementalType.PIERCING: ElementType.NONE,
    DamageElementalType.HEAL: ElementType.NONE,
}


class DamageType(str, Enum):
    """
    Enum representing the type of a damage.
    """
    DAMAGE = 'DAMAGE'
    HEAL = 'HEAL'
    ELEMENT_APPLICATION = 'ELEMENT_APPLICATION'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ObjectType(str, Enum):
    """
    Enum representing the type of an object.
    """
    EMPTY = 'EMPTY'
    CHARACTOR = 'CHARACTOR'
    DICE = 'DICE'
    CARD = 'CARD'
    SUMMON = 'SUMMON'
    SUPPORT = 'SUPPORT'
    SKILL = 'SKILL'
    WEAPON = 'WEAPON'
    ARTIFACT = 'ARTIFACT'
    TALENT = 'TALENT'
    CHARACTOR_STATUS = 'CHARACTOR_STATUS'
    TEAM_STATUS = 'TEAM_STATUS'
    ARCANE = 'ARCANE'

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class ObjectPositionType(str, Enum):
    """
    Enum representing the position of an object.
    """
    DECK = 'DECK'
    HAND = 'HAND'
    SUMMON = 'SUMMON'
    SUPPORT = 'SUPPORT'
    DICE = 'DICE'
    CHARACTOR = 'CHARACTOR'
    CHARACTOR_STATUS = 'CHARACTOR_STATUS'
    SKILL = 'SKILL'
    TEAM_STATUS = 'TEAM_STATUS'
    SYSTEM = 'SYSTEM'
    INVALID = 'INVALID'

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class FactionType(str, Enum):
    """
    Factions of charactors.
    """

    MONDSTADT = 'MONDSTADT'
    LIYUE = 'LIYUE'
    INAZUMA = 'INAZUMA'
    SUMERU = 'SUMERU'
    FONTAINE = 'FONTAINE'
    NATLAN = 'NATLAN'
    SNEZHNAYA = 'SNEZHNAYA'

    FATUI = 'FATUI'
    MONSTER = 'MONSTER'
    HILICHURL = 'HILICHURL'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class WeaponType(str, Enum):
    """
    Types of weapons.
    """

    SWORD = 'SWORD'
    CLAYMORE = 'CLAYMORE'
    POLEARM = 'POLEARM'
    CATALYST = 'CATALYST'
    BOW = 'BOW'
    OTHER = 'OTHER'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class SkillType(str, Enum):
    """
    Types of skills.
    """

    NORMAL_ATTACK = 'NORMAL_ATTACK'
    ELEMENTAL_SKILL = 'ELEMENTAL_SKILL'
    ELEMENTAL_BURST = 'ELEMENTAL_BURST'
    PASSIVE = 'PASSIVE'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ElementalReactionType(str, Enum):
    """
    Types of elemental reactions.
    """

    NONE = 'NONE'
    MELT = 'MELT'
    VAPORIZE = 'VAPORIZE'
    OVERLOADED = 'OVERLOADED'
    SUPERCONDUCT = 'SUPERCONDUCT'
    ELECTROCHARGED = 'ELECTROCHARGED'
    FROZEN = 'FROZEN'
    SWIRL = 'SWIRL'
    CRYSTALLIZE = 'CRYSTALLIZE'
    BURNING = 'BURNING'
    BLOOM = 'BLOOM'
    QUICKEN = 'QUICKEN'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class CostLabels(int, Enum):
    SWITCH_CHARACTOR = 0x1
    CARD = 0x2
    COMPANION = 0x4
    LOCATION = 0x8
    ITEM = 0x10
    ARTIFACT = 0x20
    WEAPON = 0x40
    TALENT = 0x80
    FOOD = 0x100
    ARCANE = 0x200
    NORMAL_ATTACK = 0x400
    ELEMENTAL_SKILL = 0x800
    ELEMENTAL_BURST = 0x1000
    CHARGED_ATTACK = 0x2000
    PLUNGING_ATTACK = 0x4000

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class IconType(str, Enum):
    """
    Icon types of objects. Used for display, and also for some effects, e.g.
    Vortex Vanquisher will increase 1 damage when any status, summons or 
    supports has shield icon.
    """

    # e.g. Changing Shifts
    BUFF = 'BUFF'
    # e.g. I Haven't lost yet used
    DEBUFF = 'DEBUFF'

    # e.g. Tandoori Chicken
    ATTACK = 'ATTACK'
    # e.g. Lotus Flower Crisp, Ushi
    DEFEND = 'DEFEND'
    # e.g. Crystallize, Unmovable Mountain
    SHIELD = 'SHIELD'

    # food card used for charactor, or egg used for team.
    SATIATED = 'SATIATED'

    # e.g. most of summons
    SANDGLASS = 'SANDGLASS'
    # e.g. Timmie, Liben
    STOPWATCH = 'STOPWATCH'

    # e.g. Rana, Sumeru City
    AVAILABLE = 'AVAILABLE'
    # e.g. Jade Chamber, Traveler's Handy Sword
    NONE = 'NONE'

    # with others, the status has its special icon.
    OTHERS = 'OTHERS'


class PlayerActionLabels(int, Enum):
    SKILL = 0x1
    SWITCH = 0x2
    CARD = 0x4
    TUNE = 0x8
    END = 0x10

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
