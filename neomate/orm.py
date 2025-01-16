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
                    res[key] = changes.get(value)
                elif key not in ["field_name", "type"]:
                    res[key]= value
                    
            new_properties[prop.get("field_name")] =  Types(__builtins__[prop.get('type')],**res)

            
        print(new_properties)
        return new_properties
    @classmethod 
    def compare_dicts(self, type1, type2):

        diff_keys = set(type1.keys()) - set(type2.keys())
        
        difference = {
            key:type2[key] for key in type1.keys() & type2.keys()
            if type1[key]!=type2[key]
        }
        return (diff_keys,difference)
    def set_nodename(old_nodename, new_nodename):
        return (f"""
    MATCH (schema:_Schema)
    WHERE schema.nodename = "{old_nodename}"
    SET schema.nodename = "{new_nodename}"
    """,f"""
    MATCH (o:{old_nodename})
    REMOVE o:{old_nodename}
    SET o:{new_nodename}
    """)
    def create_node_attr(self,nodename, attr_name):
        return f"""
    CREATE (a:_Property{{{self.to_dict(attr_name)}}})
    WITH a
    MATCH (b:_Schema)
    WHERE b.nodename ="{nodename}"
    CREATE (b) - [:HAS_PROPERTY] -> (a)
    """
    def delete_node_attr(nodename, attr_name):
        return f"""
    MATCH (p:_Schema)
    WHERE p.nodename = "{nodename}"
    MATCH (p) -[:HAS_PROPERTY] -> (a:_Property)
    WHERE a.field_name = "{attr_name}"
    DETACH DELETE a
    """
    def add_prop_to_node_attr(nodename,attr_name,data):
        query = f"""
    MATCH (schema:_Schema)
    WHERE schema.nodename ="{nodename}"
    MATCH (prop:_Property)
    WHERE prop.field_name = "{attr_name}"
        """
        query += f"""
        SET prop.{data[0]} = {data[1]}
        """ if isinstance(data[1],int) else f"""
        SET prop.{data[0]} = "{data[1]}"
        """
        return query
    
    