"""
With class registry, after version 4.3, new cards and charactors do not need to
be defined in corresponding folders, and they will be defined in the patch.
"""


from ...utils import import_all_modules


import_all_modules(__file__, __name__)
