from decimal import *
from datetime import *
from typing import *

from dataclasses import dataclass
from marshmallow import Schema, fields, post_load
from core.utility import SchemaUtil


################################################################
# Input concept class
################################################################
@dataclass
class InputClass:
    prompt: str = None
    attachments: List[str] = None


################################################################
# InputSchema concept class
################################################################
class InputClassSchema(Schema):
    prompt = fields.String(allow_none=True)
    attachments = fields.List(fields.String(allow_none=True), allow_none=True)

    @post_load
    def create(self, data, **kwargs):
        return SchemaUtil.create(InputClass(), data)
