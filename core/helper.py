import json
from typing import Any, Dict, Callable, List, Union
from marshmallow import Schema, fields

# Implementation of the missing helper functions from Openfabric SDK

def has_resource_fields(schema_instance: Schema) -> bool:
    """
    Check if the schema has resource fields.
    
    Args:
        schema_instance (Schema): Marshmallow schema instance
        
    Returns:
        bool: True if schema has resource fields, False otherwise
    """
    for field_name, field_type in schema_instance.fields.items():
        if isinstance(field_type, fields.Field) and field_name.startswith('resource_'):
            return True
    return False


def json_schema_to_marshmallow(json_schema: Dict[str, Any]) -> Callable[[], Schema]:
    """
    Convert JSON schema to a Marshmallow schema factory function.
    
    Args:
        json_schema (Dict[str, Any]): JSON schema definition
        
    Returns:
        Callable[[], Schema]: Function that returns a new Marshmallow schema instance
    """
    # This is a simplified implementation that returns a basic schema
    # In a real implementation, this would convert JSON schema to Marshmallow fields
    class DynamicSchema(Schema):
        class Meta:
            strict = True
    
    def factory():
        return DynamicSchema()
    
    return factory


def resolve_resources(resource_url_template: str, data: Dict[str, Any], schema_instance: Schema) -> Dict[str, Any]:
    """
    Resolve resource references in the data using the given URL template.
    
    Args:
        resource_url_template (str): URL template for resources with {reid} placeholder
        data (Dict[str, Any]): Data containing resource references
        schema_instance (Schema): Marshmallow schema instance
        
    Returns:
        Dict[str, Any]: Data with resolved resources
    """
    # This is a simplified implementation that returns the input data unchanged
    # In a real implementation, this would resolve resource references
    return data
