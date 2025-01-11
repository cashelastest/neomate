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

