"""
parse instance based on base class. When an object is registered, we will scan
all its parent class, and register it to the corresponding base class. When we
need to instantiate an object with a dict, with given base class, we will find
corresponding class and version, and instantiate it.
"""


import logging
import types
from typing import (
    Any, Dict, List, Optional, Set, Type, Union, get_type_hints, get_args
)

from ..server.consts import ObjectType
from .desc_registry import DescDictType, desc_exist, update_cost, update_desc


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
    """
    class_name = cls.__name__
    cls_type_hints = get_type_hints(cls)
    name_hints = cls_type_hints['name']
    version_hints = cls_type_hints['version']
    desc_hints = cls_type_hints['desc']
    if len(get_args(desc_hints)) == 0:
        raise AssertionError(
            f'Class {cls} desc type hint is empty or not a Literal'
        )
    descs = get_args(desc_hints)
    version = version_hints.__args__[0]
    type_hints = cls_type_hints['type']
    if len(type_hints.__args__) != 1:
        raise AssertionError(
            f'Class {cls} type hint is empty or more than 1'
        )
    obj_type = type_hints.__args__[0]
    names = name_hints.__args__
    # check if class name is match
    version_from_name = '.'.join(class_name.split('_')[-2:])
    if version_from_name != version:
        raise AssertionError(
            f'Class {cls} version {version} is not equal to version '
            f'from name {version_from_name}'
        )
    for name in names:
        desc_type = obj_type
        if obj_type == ObjectType.CHARACTOR:
            # for charactor, also check its skill descs
            instance = cls(name = name, version = version)
            for skill in instance.skills:
                skill_type = f'SKILL_{name}_{skill.skill_type}'
                if not desc_exist(skill_type, skill.name, version):
                    raise AssertionError(
                        f'Class {cls} name {name} version {version} skill '
                        f'{skill.name} is not found in descs'
                    )
                # register skill costs
                update_cost(skill_type, skill.name, version, skill.cost)
        if obj_type == ObjectType.TALENT:
            # for talent, its type name should change
            target_charactor_names = cls_type_hints['charactor_name'].__args__
            assert len(target_charactor_names) == 1
            desc_type = f'TALENT_{target_charactor_names[0]}'
        for desc in descs:
            if desc == '':
                desc_name = name
            else:
                desc_name = f'{name}_{desc}'
            if desc == '':
                # empty, no extra desc
                if not desc_exist(desc_type, desc_name, version):
                    raise AssertionError(
                        f'Class {cls} name {name} version {version} type '
                        f'{desc_type} is not found in descs'
                    )
            else:
                if not desc_exist(desc_type, desc_name, version):
                    raise AssertionError(
                        f'Class {cls} name {name}(desc: {desc}) version '
                        f'{version} is not found in descs'
                    )
            if 'cost' in cls_type_hints:
                # has cost, register it
                instance = cls(
                    name = name, version = version, position = {
                        'player_idx': -1, 'area': 'INVALID', 'id': -1
                    }
                )
                update_cost(desc_type, desc_name, version, instance.cost)
    version = _version_to_int(version)
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
                            f'Class {cls} is already registered in base class '
                            f'{base_class.__name__} registry'
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


def register_class(
        classes: Type[Any], descs: Dict[str, DescDictType] | None = None
):
    """
    Register classes with their descriptions. If classes is a Union, register
    all classes in the union. Otherwise, register the class itself.
    Before registering, descs will be updated first.
    """
    if descs is not None:
        update_desc(descs)
    if _is_union_type(classes):
        for type in classes.__args__:  # type: ignore
            register_class_one(type)
    else:
        register_class_one(classes)


def _get_class(
    class_dict: Dict[str, Dict[int, Type[Any]]], 
    class_version_list: Dict[str, List[int]], 
    name: str, version: str
):
    version_int = _version_to_int(version)
    for v in class_version_list[name]:
        if v <= version_int:
            return class_dict[name][v]
    else:
        # all failed, raise error
        raise KeyError()


def _parse_object(
    class_dict: Dict[str, Dict[int, Type[Any]]], 
    class_version_list: Dict[str, List[int]], 
    name: str, version: str, args: Any
):
    cls = _get_class(class_dict, class_version_list, name, version)
    return cls(**args)


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
                    _class_dict[type], _class_version_dict[type],
                    name, version, args
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
                _class_dict[base_class], 
                _class_version_dict[base_class], 
                name,
                version,
                args
            )
        except KeyError:
            raise AssertionError(
                f'Cannot find class {name} with version {version} in base '
                f'class {base_class}'
            )


def get_class_list_by_base_class(
    base_class: Type[Any], version: str = '99.9', exclude: Set[str] = set()
) -> List[str]:
    """
    Get list of class names by base class and version. If the base class is a 
    union type, class names that matchs any type in the union will be returned.

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
        if type not in _class_dict:
            raise AssertionError(
                f'Base class {type} is not registered in class registry'
            )
        names = _class_dict[type].keys()
        for name in names:
            if name in exclude:
                continue
            try:
                _ = _get_class(
                    _class_dict[type], 
                    _class_version_dict[type], 
                    name, 
                    version
                )
                # get class success
                result_set.add(name)
            except KeyError:
                continue
    return sorted(list(result_set))


__all__ = (
    'register_base_class', 
    'register_class', 
    'get_instance',
    'get_class_list_by_base_class',
)
