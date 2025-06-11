from neomate.NeoError import NodeAttrError
from typeguard import check_type
from neomate.Query import CypherQuery
class BaseNode:
    models = []

    @classmethod
    def create_models(cls):
        for model in cls._get_all_subclasses():
            if hasattr(model, "__dataclass_fields__"):
                for field_name in model.__dataclass_fields__:
                    if field_name != "__nodename__":
                        setattr(model, field_name, CypherQuery(field_name))
                cls.models.append(model)

    @classmethod
    def _get_all_subclasses(cls):
        subclasses = set(cls.__subclasses__())
        for subclass in list(subclasses):
            subclasses.update(subclass._get_all_subclasses())
        return subclasses

    def check_types_by_annotations(self):
        for attr, attr_type in self.__class__.__annotations__.items():
            value = getattr(self, attr)
            try:
                check_type(value, attr_type)
            except TypeError as e:
                raise NodeAttrError(self.__class__.__name__, attr, f"Type mismatch. {attr} has type {type(getattr(self,attr)).__name__} not {attr_type.__name__}")