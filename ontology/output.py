from dataclasses import dataclass
from marshmallow import Schema, fields, post_load

from core.utility import SchemaUtil


################################################################
# Output concept class
################################################################
@dataclass
class OutputClass:
    message: str = None


################################################################
# OutputSchema concept class
################################################################
class OutputClassSchema(Schema):
    message = fields.Str(allow_none=True)

    @post_load
    def create(self, data, **kwargs):
        return SchemaUtil.create(OutputClass(), data)
