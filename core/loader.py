from typing import Dict, Any, Type, Optional
from marshmallow import Schema

class OutputSchemaInst:
    """
    Class that handles output schema instantiation and validation.
    This is a simplified version of the Openfabric SDK's OutputSchemaInst class.
    """
    
    def __init__(self, schema_cls: Optional[Type[Schema]] = None):
        """
        Initialize with a schema class.
        
        Args:
            schema_cls (Type[Schema], optional): Schema class to use for validation
        """
        self.schema_cls = schema_cls
    
    def dump(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump data according to the schema.
        
        Args:
            data (Dict[str, Any]): Data to validate and dump
            
        Returns:
            Dict[str, Any]: Validated and processed data
        """
        if self.schema_cls is None:
            return data
            
        schema = self.schema_cls()
        return schema.dump(data)
    
    def load(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load and validate data according to the schema.
        
        Args:
            data (Dict[str, Any]): Data to validate and load
            
        Returns:
            Dict[str, Any]: Validated and processed data
        """
        if self.schema_cls is None:
            return data
            
        schema = self.schema_cls()
        return schema.load(data)
