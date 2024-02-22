import bisect
import logging
from typing import Any, Dict, get_args, get_type_hints

from .desc_registry import desc_exist, update_cost

from ..server.consts import ObjectType


def check_cls_valid_and_update_cost(cls: Any, obj_type: ObjectType):
    """
    Check whether this class hint and desc is valid for given class, if not, raise
    error. Then register cost information for this class.

    When registering cost, it initializes the class instance and get the cost from it.

    TODO: This function is added for compatibility with old logic, and is subject to
    refactor.
    """
    class_name = cls.__name__
    cls_type_hints = get_type_hints(cls)
    name_hints = cls_type_hints["name"]
    version_hints = cls_type_hints["version"]
    desc_hints = cls_type_hints["desc"]
    # check desc hint exist
    if len(get_args(desc_hints)) == 0:
        raise AssertionError(f"Class {cls} desc type hint is empty or not a Literal")
    descs = get_args(desc_hints)
    version = version_hints.__args__[0]
    type_hints = cls_type_hints["type"]
    if len(type_hints.__args__) != 1:
        raise AssertionError(f"Class {cls} type hint is empty or more than 1")
    obj_type = type_hints.__args__[0]
    names = name_hints.__args__
    # check if class name is match
    version_from_name = ".".join(class_name.split("_")[-2:])
    if version_from_name != version:
        raise AssertionError(
            f"Class {cls} version {version} is not equal to version "
            f"from name {version_from_name}"
        )
    for name in names:
        # check if an object can generate without name. No objects should be
        # generated without name.
        # TODO: is it necessary to distinguish?
        # direct_generate = False
        # try:
        #     instance = cls(version = version)
        #     direct_generate = True
        # except ValidationError:
        #     pass
        # if direct_generate and obj_type != ObjectType.SYSTEM:
        #     print(
        #         f"Class {cls} name {name} version {version} "
        #         "failed direct generate test"
        #     )
        desc_type = obj_type
        if obj_type == ObjectType.CHARACTER:
            # for character, also check its skill descs
            instance = cls(name=name, version=version)
            for skill in instance.skills:
                skill_type = f"SKILL_{name}_{skill.skill_type}"
                if not desc_exist(skill_type, skill.name, version):
                    raise AssertionError(
                        f"Class {cls} name {name} version {version} skill "
                        f"{skill.name} is not found in descs"
                    )
                # register skill costs
                update_cost(skill_type, skill.name, version, skill.cost)
        if obj_type == ObjectType.TALENT:
            # for talent, its type name should change
            target_character_names = cls_type_hints["character_name"].__args__
            assert len(target_character_names) == 1
            desc_type = f"TALENT_{target_character_names[0]}"
        for desc in descs:
            if desc == "":
                desc_name = name
            else:
                desc_name = f"{name}_{desc}"
            if desc == "":
                # empty, no extra desc
                if not desc_exist(desc_type, desc_name, version):
                    raise AssertionError(
                        f"Class {cls} name {name} version {version} type "
                        f"{desc_type} is not found in descs"
                    )
            else:
                if not desc_exist(desc_type, desc_name, version):
                    raise AssertionError(
                        f"Class {cls} name {name}(desc: {desc}) version "
                        f"{version} is not found in descs"
                    )
            if "cost" in cls_type_hints:
                # has cost, register it
                instance = cls(
                    name=name,
                    version=version,
                    position={"player_idx": -1, "area": "INVALID", "id": -1},
                )
                update_cost(desc_type, desc_name, version, instance.cost)


class InstanceFactory:
    instance_register = {}

    def __init__(self):
        self._instance_list = []
        self._instance_list_sorted = False

    def register_instance(self, cls: Any):
        """
        Register one class. If the class is registered, print a warning. If same
        version, name and base class, raise error.
        """
        cls_type_hints = get_type_hints(cls)
        version = cls_type_hints["version"].__args__[0]
        obj_type = cls_type_hints["type"].__args__[0]
        names = cls_type_hints["name"].__args__
        for name in names:
            check_cls_valid_and_update_cost(cls, obj_type)
            key = "%s+%s+%s" % (obj_type, name, version)
            if key in self.instance_register:
                if self.instance_register[key] == cls:
                    logging.warning(
                        f"Class {cls} is already registered in instance factory"
                    )
                else:
                    raise AssertionError(
                        f"Class {cls} and {self.instance_register[key]} have "
                        "same version and name"
                    )
            self.instance_register[key] = cls
            self._instance_list.append(key)
            self._instance_list_sorted = False

    def get_instance(self, base_class: Any, args: Dict):
        cls_type_hints = get_type_hints(base_class)
        obj_types = cls_type_hints["type"].__args__
        name = args["name"]
        version = args.get("version", "99.9")
        keys = []
        for obj_type in obj_types:
            keys.append("%s+%s+%s" % (obj_type, name, version))
        if not self._instance_list_sorted:
            self._instance_list.sort()
            self._instance_list_sorted = True
        instance_list = self._instance_list
        for key in keys:
            cls_key_idx = bisect.bisect_right(instance_list, key)
            if cls_key_idx == len(instance_list):
                cls_key_idx -= 1
            if instance_list[cls_key_idx] > key:
                cls_key_idx -= 1
            cls_key = instance_list[cls_key_idx]
            if self._is_same_instance(key, cls_key):
                cls = self.instance_register[cls_key]
                exact_version = cls_key.split("+")[2]
                args["version"] = exact_version
                return cls(**args)
            else:
                continue

        raise KeyError("Instance %s+%s not found in instance factory" % (name, version))

    @staticmethod
    def _is_same_instance(key1, key2):
        """
        Check whether type and name are the same.
        """
        info1 = key1.split("+")
        info2 = key2.split("+")
        if info1[0] == info2[0] and info1[1] == info2[1]:
            return True
        else:
            return False
