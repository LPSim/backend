"""
parse instance based on base class. When an object is registered, we will scan
all its parent class, and register it to the corresponding base class. When we
need to instantiate an object with a dict, with given base class, we will find
corresponding class and version, and instantiate it.
"""


import logging
import types
from typing import Any, Dict, List, Optional, Set, Type, Union, get_type_hints, get_args

from .instance_factory import InstanceFactory
from ..server.consts import ObjectType
from .desc_registry import DescDictType, desc_exist, update_cost, update_desc
instance_factory = InstanceFactory()

"""
The dict to save all registered classes. Key is the base class, value is a dict
with key as name, value is a dict with version as name, and value as class.
In class version dict, it saves all available version of a card, and is sorted
descendingly.
"""
_class_dict: Dict[Type[Any], Dict[str, Dict[int, Type[Any]]]] = {}
_class_version_dict: Dict[Type[Any], Dict[str, List[int]]] = {}
"""
The set that contains all registered base classes.
"""
_class_set = set()


def _is_union_type(t) -> bool:
    return (
        getattr(t, "__class__", None) == types.UnionType
        or getattr(t, "__origin__", None) is Union
        or getattr(t, "__origin__", None) is Optional
    )


def register_base_class(base_class: Type[Any]):
    """
    Register a base class.
    """
    return


def register_class(classes: Type[Any], descs: Dict[str, DescDictType] | None = None):
    """
    Register classes with their descriptions. If classes is a Union, register
    all classes in the union. Otherwise, register the class itself.
    Before registering, descs will be updated first.
    """
    if descs is not None:
        update_desc(descs)
    if _is_union_type(classes):
        for type in classes.__args__:  # type: ignore
            instance_factory.register_instance(type)
    else:
        instance_factory.register_instance(classes)


# def get_instance_from_type_unions(types, args, key = 'name'):
def get_instance(base_class: Type[Any], args: Dict):
    """
    Get instance from registry. If the base class is a union type, we will try
    each type sequentially.
    """
    base_class_list = [base_class]
    if _is_union_type(base_class):
        base_class_list = base_class.__args__
    for cls in base_class_list:
        try:
            return instance_factory.get_instance(cls, args)
        except Exception as e:
            print(e)
            continue

    names = [x.__name__ for x in base_class_list]
    raise AssertionError("Instance %s not found in instance factory with args %s" % (names, args))


def get_class_list_by_base_class(
    base_class: Type[Any], version: str = "99.9", exclude: Set[str] = set()
) -> List[str]:
    """
    Get list of class names by base class and version. If the base class is a
    union type, class names that matches any type in the union will be returned.

    Args:
        base_class: The base class to search.
        version: The version of the class. Classes that have higher version
            than this will be ignored. Default is '99.9'.
        exclude: Exclude class with specified names in the list.

    Return:
        List of class names.
    """
    result_set: Set[str] = set()
    base_class_list = [base_class]
    if _is_union_type(base_class):
        # is union type, try each class sequentially
        base_class_list = base_class.__args__  # type: ignore
    for type in base_class_list:
        for key in instance_factory.instance_register.keys():
            name = key.split("+")[1]
            if name in exclude:
                continue
            if issubclass(instance_factory.instance_register[key], type):
                result_set.add(name)
    return sorted(list(result_set))


__all__ = (
    "register_base_class",
    "register_class",
    "get_instance",
    "get_class_list_by_base_class",
)