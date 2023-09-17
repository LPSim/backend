import pydantic
from typing import List


class BaseModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid  # default forbid extra fields


def get_instance_from_type_unions(types, args):
    """
    Get instance from type unions.
    """
    class TempClass(BaseModel):
        obj: types
    return TempClass(obj = args).obj


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


if __name__ == "__main__":
    pass
