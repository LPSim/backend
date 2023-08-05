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


class DamageType(str, Enum):
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

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


ELEMENT_TO_DAMAGE_TYPE = {
    ElementType.NONE: DamageType.PHYSICAL,
    ElementType.CRYO: DamageType.CRYO,
    ElementType.HYDRO: DamageType.HYDRO,
    ElementType.PYRO: DamageType.PYRO,
    ElementType.ELECTRO: DamageType.ELECTRO,
    ElementType.GEO: DamageType.GEO,
    ElementType.DENDRO: DamageType.DENDRO,
    ElementType.ANEMO: DamageType.ANEMO,
}
DAMAGE_TYPE_TO_ELEMENT = {
    DamageType.CRYO: ElementType.CRYO,
    DamageType.HYDRO: ElementType.HYDRO,
    DamageType.PYRO: ElementType.PYRO,
    DamageType.ELECTRO: ElementType.ELECTRO,
    DamageType.GEO: ElementType.GEO,
    DamageType.DENDRO: ElementType.DENDRO,
    DamageType.ANEMO: ElementType.ANEMO,
    DamageType.PHYSICAL: ElementType.NONE,
    DamageType.PIERCING: ElementType.NONE,
}


class ObjectType(str, Enum):
    """
    Enum representing the type of an object.
    """
    EMPTY = 'EMPTY'
    CHARACTOR = 'CHARACTOR'
    DIE = 'DIE'
    DECK_CARD = 'DECK_CARD'
    HAND_CARD = 'HAND_CARD'
    SUMMON = 'SUMMON'
    SUPPORT = 'SUPPORT'
    SKILL = 'SKILL'
    WEAPON = 'WEAPON'
    ARTIFACT = 'ARTIFACT'
    TALENT = 'TALENT'
    CHARACTOR_STATUS = 'CHARACTOR_STATUS'
    TEAM_STATUS = 'TEAM_STATUS'

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


class SkillType(str, Enum):
    """
    Types of skills.
    """

    NORMAL_ATTACK = 'NORMAL_ATTACK'
    ELEMENTAL_SKILL = 'ELEMENTAL_SKILL'
    ELEMENTAL_BURST = 'ELEMENTAL_BURST'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class AttackType(str, Enum):
    """
    Types of attacks.
    """

    NORMAL = 'NORMAL'
    CHARGED = 'CHARGED'
    PLUNGING = 'PLUNGING'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class DamageSourceType(str, Enum):
    """
    Types of damage sources. Current player means the player doing action.
    """

    CURRENT_PLAYER_CHARACTOR = 'CURRENT_PLAYER_CHARACTOR'
    CURRENT_PLAYER_SUMMON = 'CURRENT_PLAYER_SUMMON'
    CURRENT_PLAYER_SUPPORT = 'CURRENT_PLAYER_SUPPORT'
    CURRENT_PLAYER_CHARACTOR_STATUS = 'CURRENT_PLAYER_CHARACTOR_STATUS'
    CURRENT_PLAYER_TEAM_STATUS = 'CURRENT_PLAYER_TEAM_STATUS'
    CURRENT_PLAYER_WEAPON = 'CURRENT_PLAYER_WEAPON'
    CURRENT_PLAYER_ARTIFACT = 'CURRENT_PLAYER_ARTIFACT'
    CURRENT_PLAYER_TALENT = 'CURRENT_PLAYER_TALENT'
    ENEMY_PLAYER_CHARACTOR = 'ENEMY_PLAYER_CHARACTOR'
    ENEMY_PLAYER_SUMMON = 'ENEMY_PLAYER_SUMMON'
    ENEMY_PLAYER_SUPPORT = 'ENEMY_PLAYER_SUPPORT'
    ENEMY_PLAYER_CHARACTOR_STATUS = 'ENEMY_PLAYER_CHARACTOR_STATUS'
    ENEMY_PLAYER_TEAM_STATUS = 'ENEMY_PLAYER_TEAM_STATUS'
    ENEMY_PLAYER_WEAPON = 'ENEMY_PLAYER_WEAPON'
    ENEMY_PLAYER_ARTIFACT = 'ENEMY_PLAYER_ARTIFACT'
    ENEMY_PLAYER_TALENT = 'ENEMY_PLAYER_TALENT'

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
