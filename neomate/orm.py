from dataclasses import dataclass
from typing import Union, Any, Optional,Type


@dataclass
class Types:

    type:Union[Type, str]
    name:Optional[str] = None
    default:Any = None
    is_must_have:bool = True
    relate_name:Optional[str]=None
    bidiractional:bool=False
    insert_none:bool = True
    
    def actual_type(self):
        """Resolves the actual Python type for validation.

    If type is string, attempts to import it from __main__.
    Used for handling forward references in type annotations.

    Returns:
        Type: Actual Python type to validate against

    Raises:
        AttributeError: If string type cannot be imported from __main__
    """
        if isinstance(self.type,str):
            return getattr(__import__('__main__'), self.type)
        return self.type
    def to_dict(self,keys):
        res = {}
        changes = {
            "true":True,
            "false":False
            
        }
        for key, value in vars(self).items():

            if key == "type":
                res[key] = value.__name__
            elif value in changes.keys():
                res[key] = changes[value]
            # elif key == "name":

            #     res[key] = value if value is not None else keys
            
            else:
                res[key] = value
                
        res["field_name"] = keys
        return ", ".join(f"""{k}:"{v}" """ for k,v in res.items())
    @classmethod
    def from_dict(self, schema):
        nodename = schema.get("schema").get("nodename")
        properties = schema.get("properties")
        new_properties = {"__nodename__":nodename}
        changes = {
            "True":True,
            "False":False,
            'None':None,
            "none":None,
            "true":True,
            "false":False
            
        }
        for prop in properties:
            res = {}        

            for key,value in prop.items():
                if str(value).lower() in changes.keys():
                    print(1)
                    res[key] = changes[value]
                elif key not in ["field_name", "type"]:
                    res[key]= value
                    
            new_properties[prop.get("field_name")] =  Types(__builtins__[prop.get('type')],**res)

            
        print(new_properties)
        return new_properties
            
    