from core.base import NeoBase
from core.orm import Types

class Base:
    id  = 0

    def to_dict(self)->list[dict]:
        """Generates a list of dictionaries based on object attributes and its nested objects.

    Creates dictionary representation of the object, including:
    - Basic attributes and their values
    - Nested objects (recursively converted to dictionaries)
    - Special handling of None values and custom objects

    Returns:
        list[dict]: List of dictionaries where:
            - First elements are nested object dictionaries (if any)
            - Last element is current object dictionary with fields:
                - NODE_TYPE: class name or __nodename__ if specified
                - All non-None attributes as key-value pairs
    """
        result = {"NODE_TYPE":self.__class__.__name__ if "__nodename__" not in vars(self.__class__) else self.__nodename__}
        reverse_map = {
            name:getattr(getattr(self.__class__,name), "name", name)
            for name in vars(self.__class__)
            if isinstance(getattr(self.__class__, name), Types)
            and getattr(getattr(self.__class__, name), "name") is not None
        }
        nodes = []
        for key, value in vars(self).items():
            key = reverse_map.get(key,key)
            if value is None or key == "None":
                continue
            if hasattr(value, "to_dict") and value.__class__.__module__ != 'builtins':
                result[key] = value.name if hasattr(value, 'name') else value.id
                nested_dict = value.to_dict()
                if isinstance(nested_dict, list):
                    nodes.extend(nested_dict)
                else:
                    nodes.append(nested_dict)
                continue
            result[key] = str(value)
        nodes.append(result)

        return nodes


class NeoMate(NeoBase):
    def __init__(self,session):
        self.base = Base
        super().__init__(session = session)
    
    
    def validate(self, schema:dict, kwargs:dict)->dict|None:
        """Validates data against provided schema and prepares it for database insertion.

    Args:
        schema (dict): Schema dictionary where:
            - Keys are field names
            - Values are Types instances defining field rules
        kwargs (dict): Data to validate against schema

    Returns:
        list[dict]: List of validated dictionaries ready for insertion:
            - Nested objects are processed recursively
            - Type validations are applied
            - Default values are inserted where specified

    Raises:
        Exception: If field is missing in schema
        Exception: If value type doesn't match schema type
        Exception: If required field is missing and has no default
    """
        answer = []
        kwargs = {k:v for k,v in kwargs.items() 
                if k and v is not None
                and schema.get(k) is not None
                and schema[k].insert_none
        }
        
        for key, value in kwargs.items():
            validate_data = schema.get(key, None)
            if validate_data is None:
                raise Exception(f"""Error in data: no such field: '{key}' in scheme""")
            if not isinstance(value, validate_data.actual_type()):
                raise Exception(f"ERROR in data: {key}-{value}\n{value} must be {validate_data.type}")
            if validate_data.actual_type().__module__ != 'builtins':
                kwargs[key] = value.name if hasattr(value, 'name') else value.id
                answer.extend(value.to_dict())
            del schema[key]
        if len(schema) == 0:
            answer.append(kwargs)
            return answer
        
        for key, element in schema.items():
            if type(element) is not Types:
                continue
            if element.default is not None:
                kwargs[element.name or key] = element.default
                continue
            if not element.is_must_have:
                continue
            raise Exception(f"Validation Error: no data for {key} in your query")
        answer.append(kwargs)
        return answer
    
    
    def create_node(self,cls:object, **kwargs):
        """creates node based on object wit hvalidation by schema

        Args:
            cls (object): object, which will be checked, and created node
        """
        data = {key:value
                for base in type(cls).__mro__
                for key, value in vars(base).items()
                if not key.startswith("__") or key == "__nodename__"
                }
        el_type = data.get("__nodename__", type(cls).__name__)
        data.pop('__nodename__', None)
        if len(vars(cls)) !=0:
            kwargs = vars(cls)
        try:
            res = self.validate(data, kwargs)
        except Exception:

            self.logger.exception("Validation failed")
            raise 
        try:
            self.add_nodes(el_type, res)
            self.logger.info("Success!")
        except:
            self.logger.error("error")

