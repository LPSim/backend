import pydantic
from typing import List
from .class_registry import get_instance_from_type_unions  # noqa: F401


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


if __name__ == "__main__":
    pass
