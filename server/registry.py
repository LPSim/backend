from server.event import Events


class Registry:

    def __init__(self):
        self._registry = {}
        self._id_counter = 0
        self.event_triggers = {}
        for i in Events:
            self.event_triggers[i] = []

    def register(self, obj):
        """
        Register an object to the registry.
        """
        self._registry[self._id_counter] = obj
        self._id_counter += 1
        for i in obj.event_triggers:
            self.event_triggers[i].append(self._id_counter)

    def find_object(self, object_id):
        """
        Find an object by its ID.
        """
        return self._registry[object_id]

    def find_id(self, obj):
        """
        Find the ID of an object.
        """
        for i in self._registry:
            if self._registry[i] == obj:
                return i

    def destroy(self, obj):
        """
        Destroy an object from the registry.
        """
        obj_id = self.find_id(obj)
        for i in obj.event_triggers:
            self.event_triggers[i].remove(obj_id)
        self._registry.pop(obj_id)
