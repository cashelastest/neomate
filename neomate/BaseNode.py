from neomate.NeoError import NodeAttrError
from typeguard import check_type
class BaseNode:

    def check_types_by_annotations(self):
        for attr, attr_type in self.__class__.__annotations__.items():
            value = getattr(self, attr)
            try:
                check_type(value, attr_type)
            except TypeError as e:
                raise NodeAttrError(self.__class__.__name__, attr, f"Type mismatch. {attr} has type {type(getattr(self,attr)).__name__} not {attr_type.__name__}")