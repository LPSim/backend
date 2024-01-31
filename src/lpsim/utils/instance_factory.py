from typing import Any, Dict, Type, get_type_hints


class InstanceFactory:
    instance_register = {}

    def register_instance(self, cls: Type[Any]):
        """
        Register one class. If the class is registered, print a warning. If same
        version, name and base class, raise error.
        """
        cls_type_hints = get_type_hints(cls)
        version = cls_type_hints["version"].__args__[0]
        obj_type = cls_type_hints["type"].__args__[0]
        names = cls_type_hints["name"].__args__
        for name in names:
            key = "%s+%s+%s" % (obj_type, name, version)
            self.instance_register[key] = cls

    def get_instance(self, base_class: Type[Any], args: Dict):
        cls_type_hints = get_type_hints(base_class)
        obj_types = cls_type_hints["type"].__args__
        name = args["name"]
        version = args.get("version", "99.9")
        keys = []
        for obj_type in obj_types:
            keys.append("%s+%s+%s" % (obj_type, name, version))
        instance_list = [x for x in self.instance_register.keys()]
        instance_list.sort()
        for key in keys:
            for i in range(len(instance_list) - 1):
                if key < instance_list[i + 1]:
                    if self._is_same_instance(key, instance_list[i]):
                        """
                        Type and name same and version is lower than the next, should
                        be current object.
                        """
                        cls = self.instance_register[instance_list[i]]
                        exact_version = instance_list[i].split("+")[2]
                        args["version"] = exact_version
                        return cls(**args)
                    else:
                        break
            if self._is_same_instance(key, instance_list[-1]):
                cls = self.instance_register[instance_list[-1]]
                return cls(**args)

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
