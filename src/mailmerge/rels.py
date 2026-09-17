from copy import deepcopy

# import locale
from .constants import NAMESPACES


class RelationsDocument:
    """handling relations document"""

    def __init__(self, rel_part):
        self.rel_part = rel_part

    def replace_relation(self, merge_data, old_relation_elem, new_target):
        root = self.rel_part.getroot()
        new_relation = deepcopy(old_relation_elem)
        # print(etree.tostring(new_relation))
        new_relation.attrib["Id"] = merge_data.unique_id_manager.register_id_str(new_relation.attrib["Id"])
        # print(old_relation_elem.attrib['Id'], "->", new_relation.attrib['Id'])
        new_relation.attrib["Target"] = new_target
        root.append(new_relation)
        return new_relation.attrib["Id"]

    def get_relation_elem(self, target):
        """returns the relation element for the"""
        return self.rel_part.getroot().find('rr:Relationship[@Target="%s"]' % target, namespaces=NAMESPACES)

    def get_all(self):
        """returns all relations"""
        return self.rel_part.getroot().xpath("rr:Relationship", namespaces=NAMESPACES)
