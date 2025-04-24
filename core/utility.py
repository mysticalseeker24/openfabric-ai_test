from copy import deepcopy
from typing import Any, Dict, Type, TypeVar, cast

T = TypeVar('T')

class SchemaUtil:
    """
    Utility class for marshmallow schema operations.
    Local implementation of the Openfabric SDK SchemaUtil class.
    """
    
    @staticmethod
    def create(obj: T, data: Dict[str, Any]) -> T:
        """
        Create an object with data applied to it.
        
        Args:
            obj: The target object to populate
            data: Dictionary of attribute values to apply
            
        Returns:
            The populated object
        """
        instance = deepcopy(obj)
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance
