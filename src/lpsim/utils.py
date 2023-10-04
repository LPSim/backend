import pydantic
from typing import List, get_type_hints


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


"""
parse instance in unions. as hundreds of classes are included in the union,
to accelerate parse speed, we split the union into several unions by their
name.
"""


# key: a union. value: a dict. key: name literal. value: class unions.
_union_dict = {}


def _create_new_dict(types, key: str):
    new_dict = {}
    for type in types.__args__:
        name_hints = get_type_hints(type)[key]
        for name in name_hints.__args__:
            if name not in new_dict:
                new_dict[name] = type
            new_dict[name] |= type
    _union_dict[types] = new_dict


def get_instance_from_type_unions(types, args, key = 'name'):
    """
    Get instance from type unions.
    """
    if types not in _union_dict:
        # print('new', args['name'])
        _create_new_dict(types, key)
    target_types = _union_dict[types][args[key]]
    return pydantic.parse_obj_as(target_types, args)


if __name__ == "__main__":
    pass
