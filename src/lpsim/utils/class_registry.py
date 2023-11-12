"""
parse instance based on base class. When an object is registered, we will scan
all its parent class, and register it to the corresponding base class. When we
need to instantiate an object with a dict, with given base class, we will find
corresponding class and version, and instantiate it.
"""


import logging
import types
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints

import pydantic


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
        getattr(t, '__class__', None) == types.UnionType
        or getattr(t, '__origin__', None) is Union 
        or getattr(t, '__origin__', None) is Optional
    )


def _version_to_int(version: str) -> int:
    """
    Convert version string to int. For example, 3.2 will be converted to
    32
    """
    return int(float(version) * 10 + 0.1)


def register_base_class(base_class: Type[Any]):
    """
    Register a base class.
    """
    _class_dict[base_class] = {}
    _class_version_dict[base_class] = {}
    _class_set.add(base_class)


def register_class_one(cls: Type[Any]):
    """
    Register one class. If the class is registered, print a warning. If same
    version, name and base class, raise error. If descs not exist, raise error.
    TODO: currently not dealing with descs.
    TODO: for chartactors, check their talent type hint is original
    """
    class_name = cls.__name__
    cls_type_hints = get_type_hints(cls)
    name_hints = cls_type_hints['name']
    version_hints = cls_type_hints['version']
    assert len(version_hints.__args__) == 1
    version = version_hints.__args__[0]
    names = name_hints.__args__
    # check if class name is match
    version_from_name = '.'.join(class_name.split('_')[-2:])
    if version_from_name != version:
        raise AssertionError(
            f'Class {cls} version {version} is not equal to version '
            f'from name {version_from_name}'
        )
    version = _version_to_int(version)
    for name in names:
        # TODO check descs
        ...
    register_success = False
    base_classes = cls.mro()
    for base_class in base_classes:
        if base_class in _class_set:
            if base_class.__name__ == 'CharactorBase':
                # is a charactor, check if talent type hint is original
                talent_hint = cls_type_hints['talent']
                assert len(talent_hint.__args__) == 2
                assert talent_hint.__args__[0].__name__ == 'TalentBase', (
                    cls
                )
                assert talent_hint.__args__[1] is type(None)
            register_success = True
            for name in names:
                if name not in _class_dict[base_class]:
                    _class_dict[base_class][name] = {}
                    _class_version_dict[base_class][name] = []
                target_dict = _class_dict[base_class][name]
                target_version_dict = _class_version_dict[base_class][name]
                if version in target_dict:
                    if target_dict[version] == cls:
                        logging.warning(
                            f'Class {cls} is already registered in class '
                            'registry'
                        )
                        continue
                    else:
                        raise AssertionError(
                            f'Class {cls} and {target_dict[version]} have '
                            'same version and name'
                        )
                target_dict[version] = cls
                target_version_dict.append(version)
                target_version_dict.sort(reverse = True)
    if not register_success:
        raise AssertionError(
            f'Class {cls} is not registered in class registry, '
            'No base class is matched.'
        )


def register_class(classes: Type[Any], descs: Dict | None = None):
    """
    Register classes with their descriptions. If classes is a Union, register
    all classes in the union. Otherwise, register the class itself.
    Before registering, descs will be updated first.
    """
    ...  # TODO deal descs
    if _is_union_type(classes):
        for type in classes.__args__:  # type: ignore
            register_class_one(type)
    else:
        register_class_one(classes)


def _parse_object(
    class_dict: Dict[int, Type[Any]], class_version_dict: List[int], 
    version: str, args: Any
):
    version_int = _version_to_int(version)
    for v in class_version_dict:
        if v <= version_int:
            return pydantic.parse_obj_as(class_dict[v], args)
    else:
        # all failed, raise error
        raise KeyError()


# def get_instance_from_type_unions(types, args, key = 'name'):
def get_instance(base_class: Type[Any], args: Dict):
    """
    Get instance from registry. If the base class is a union type, we will try
    each type sequentially.
    """
    name = args['name']
    version = args.get('version', '99.9')
    if _is_union_type(base_class):
        # is union type, try each class sequentially
        for type in base_class.__args__:  # type: ignore
            if type not in _class_dict:
                raise AssertionError(
                    f'Base class {type} is not registered in class registry'
                )
            try:
                return _parse_object(
                    _class_dict[type][name], _class_version_dict[type][name],
                    version, args
                )
            except KeyError:
                continue
        raise AssertionError(
            f'Cannot find class {name} in union type {base_class}'
        )
    else:
        if base_class not in _class_dict:
            raise AssertionError(
                f'Base class {base_class} is not registered in class registry'
            )
        try:
            return _parse_object(
                _class_dict[base_class][name], 
                _class_version_dict[base_class][name], 
                version,
                args
            )
        except KeyError:
            raise AssertionError(
                f'Cannot find class {name} in base class {base_class}'
            )


__all__ = ('register_base_class', 'register_class', 'get_instance')
