import pydantic
import os
import importlib
from typing import List
from .class_registry import get_instance  # noqa: F401


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
        if file not in exceptions:
            importlib.import_module('.' + file, package = name)


if __name__ == "__main__":
    pass
