"""
Collect descriptions.
"""
import json
import logging
from typing import Any, Dict, Literal, TypedDict


ExpectedLanguageType = Literal['zh-CN', 'en-US']


class DescDictType(TypedDict, total = False):
    """
    image_path: optional, image path
    id: optional, id for sorting cards
    names: name of the card, key is language type, value is name
    descs: description of the card, key is version, value is dict of language
        type and description
    cost: cost of the card, key is version, value is dict of Cost type
    """
    image_path: str
    id: int
    names: Dict[ExpectedLanguageType, str]
    descs: Dict[str, Dict[ExpectedLanguageType, str]]
    cost: Dict[str, Dict[str, Any]]


_default_json_path = __file__[:-len('desc_registry.py')] + 'default_desc.json'
_desc_dict: Dict[str, DescDictType] = json.load(
    open(_default_json_path, 'r', encoding = 'utf-8')
)


def _parse_value(value: Any):
    """
    If value is str and starts with $: it is a reference to current desc, 
    return its referenced result. Reference key format is:
    $key1|key2|key3 ...
    """
    if isinstance(value, str) and value.startswith('$'):
        # return referenced result
        keys = value[1:].split('|')
        root = _desc_dict
        for key in keys:
            if key not in root:
                raise ValueError(f'in "{value}": key "{key}" not found')
            root = root[key]
        return root
    return value


def _merge_dict(source, destination, prev_key: str = ''):
    for key, value in source.items():
        if prev_key == '':
            pkey = key
        else:
            pkey = f'{prev_key}|{key}'
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            _merge_dict(value, node, prev_key = pkey)
        else:
            value = _parse_value(value)
            if '|names|' in pkey and value in ['', 'XXX']:
                # name is empty, raise error.
                raise ValueError(
                    f'name value "{value}" of key "{pkey}" is empty'
                )
            if key in destination:
                if destination[key] != value:
                    raise ValueError(
                        f'value "{destination[key]}" of key "{pkey}" '
                        f'is replaced by new value "{value}"'
                    )
                else:
                    logging.warning(f'duplicate adding key "{pkey}"')
            destination[key] = value
    return destination


def update_desc(desc_dict: Dict[str, DescDictType]) -> None:
    """
    Update descriptions.
    """
    _merge_dict(desc_dict, _desc_dict)


def desc_exist(type: str, name: str, version: str) -> bool:
    """
    Check if the description of the class exists.
    """
    full_name = f'{type}/{name}'
    return (
        full_name in _desc_dict 
        and 'descs' in _desc_dict[full_name]
        and version in _desc_dict[full_name]['descs']  # type: ignore
    )


def get_desc_patch() -> Dict[str, DescDictType]:
    """
    Get desc patch.
    """
    return _desc_dict


def update_cost(type: str, name: str, version: str, cost: Any) -> None:
    """
    update cost into desc dict.
    """
    if not desc_exist(type, name, version):
        raise ValueError(f'cannot find desc for {type}/{name}/{version}')
    full_name = f'{type}/{name}'
    d = _desc_dict[full_name]
    if 'cost' not in _desc_dict[full_name]:
        d['cost'] = {}
    d['cost'][version] = cost.dict()  # type: ignore


__all__ = [
    'DescDictType', 'ExpectedLanguageType', 'update_desc', 'desc_exist',
    'get_desc_patch', 'update_cost'
]
