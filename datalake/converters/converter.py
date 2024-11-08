import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List
import avro.schema

@dataclass
class NumericField:
    name: str
    is_integer: bool
    as_string: bool

"""
Base class for all converters. Allows to add postprocessing and extracting additional fields.
Also includes list of numeric fields which should be converted to double instead of 
{scale:, value:} json notation by debezium.
"""
class Converter:
    def __init__(self, schema_name, numeric_fields:List[NumericField]=[], ignored_fields=[], strict=True, updates_enabled=False):
        with open(schema_name, "rb") as s:
            self.schema = avro.schema.parse(s.read())
        self.numeric_fields = {}
        for f in numeric_fields: # fields to convert from {scale:, value:} to string
            self.numeric_fields[f.name] = f
        self.ignored_fields = ignored_fields
        self.strict = strict
        # flag to handle updates in Debezium stream
        self.updates_enabled = updates_enabled

    def timestamp(self, obj) -> int:
        raise NotImplementedError("timestamp method should be implemented in a subclass")
    
    def partition(self, obj) -> str:
        return datetime.fromtimestamp(self.timestamp(obj), tz=timezone.utc).strftime('%Y%m%d')

    def convert(self, obj, table_name=None):
        for field in self.ignored_fields:
            if field in obj:
                del obj[field]
        for field in self.numeric_fields:
            if field not in obj:
                continue
            numeric = obj[field]
            metadata = self.numeric_fields[field]
            if numeric is not None:
                assert type(numeric) == dict and 'value' in numeric and 'scale' in numeric, f"Wrong format for numeric value: {numeric}"
                decoded = int.from_bytes(base64.b64decode(numeric['value']), 'big') / pow(10, numeric['scale'])
                if metadata.is_integer:
                    decoded = int(decoded)
                obj[field] = str(decoded) if metadata.as_string else decoded
        return obj
    
    """
    Name for the table
    """
    def name(self):
        return self.schema.name
