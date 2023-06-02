from server.virtual_card_base import VirtualCardBase


class CardBase(VirtualCardBase):
    """
    Base class of all real cards. 
    """
    pass


Cards = CardBase | CardBase
