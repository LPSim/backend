"""
All status.
"""

from ..object_base import TeamStatusBase, CharactorStatusBase


TeamStatus = TeamStatusBase | TeamStatusBase
CharactorStatus = CharactorStatusBase | CharactorStatusBase
