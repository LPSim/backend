import pydantic
import os
import importlib
from typing import List, Literal, get_origin, get_type_hints
from .class_registry import (  # noqa: F401
    register_class, get_instance, get_class_list_by_base_class
)
from .desc_registry import (  # noqa: F401
    DescDictType, ExpectedLanguageType, update_desc, desc_exist,
    get_desc_patch,
)
from .deck_code import (  # noqa: F401
    deck_code_to_deck_str, deck_str_to_deck_code
)


class BaseModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid  # default forbid extra fields


def list_unique_range_right(data: List[int], minn: int, maxn: int) -> bool:
    """
    Check if the list is unique and in range [minn, maxn).
    """
    if len(data) != len(set(data)):
        return False
    for i in data:
        if i < minn or i >= maxn:
            return False
    return True


def import_all_modules(
    py_file: str,
    name: str,
    exceptions: set[str] = set()
) -> None:
    """
    This function is used to activate all modules in the directory for __init__
    and they can do default actions, i.e. register themselves to the class
    registry. To expose inner modules and classes, cannot use this function,
    import manually instead.
    """
    for file in os.listdir(os.path.dirname(py_file)):
        if file[0] == '_' or file[0] == '.':
            continue
        if file.endswith('.py'):
            file = file[:-3]
        if file not in exceptions:  # pragma: no branch
            importlib.import_module('.' + file, package = name)


def accept_same_or_higher_version(cls, v: str, values):
    msg = 'version annotation must be Literal with one str'
    if not isinstance(v, str):
        raise ValueError(msg)
    version_hints = get_type_hints(cls)['version']
    if get_origin(version_hints) != Literal:
        raise ValueError(msg)
    version_hints = version_hints.__args__
    if len(version_hints) > 1:
        raise ValueError(msg)
    version_hint = version_hints[0]
    if values['strict_version_validation'] and v != version_hint:
        raise ValueError(
            f'version {v} is not equal to {version_hint}'
        )
    if v < version_hint:
        raise ValueError(
            f'version {v} is lower than {version_hint}'
        )
    return version_hint


if __name__ == "__main__":
    pass
