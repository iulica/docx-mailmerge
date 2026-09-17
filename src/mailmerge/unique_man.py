import re

IDSTR_RE = re.compile(r"([A-Za-z_]+)(\d+)")


class UniqueIdsManager:
    """handles different counters for various ids in the document"""

    def __init__(self):
        self.id_type_map = {}  # type of id -> {'max': max_id, 'ids': set(existing_ids)}

    def register_id(self, id_type, obj_id=None):
        """registers an new object id or creates a new id for the type"""
        type_id_value = self.id_type_map.setdefault(id_type, {"max": 0, "ids": set()})
        new_obj_id = None
        if obj_id is None or obj_id in type_id_value["ids"]:
            obj_id = type_id_value["max"] + 1
            new_obj_id = obj_id
        type_id_value["ids"].add(obj_id)
        type_id_value["max"] = max(type_id_value["max"], obj_id)
        # print("registered", id_type, obj_id, new_obj_id, "max", type_id_value['max'])
        return new_obj_id

    def register_id_str(self, id_str):
        """registers directly a string of format 'type1231' where the id_type is before the id"""
        match = IDSTR_RE.match(id_str)
        assert match
        id_type, obj_id = match.groups()
        new_obj_id = self.register_id(id_type, obj_id=int(obj_id))
        if new_obj_id is not None:
            # print(id_type, obj_id, new_obj_id, self.id_type_map[id_type])
            return "%s%d" % (id_type, new_obj_id)
