import base64
from datetime import datetime, timezone
import avro.schema

"""
Base class for all converters. Allows to add postprocessing and extracting additional fields.
Also includes list of numeric fields which should be converted to double instead of 
{scale:, value:} json notation by debezium.
"""
class Converter:
    def __init__(self, schema_name, numeric_fields=[], ignored_fields=[], strict=True):
        with open(schema_name, "rb") as s:
            self.schema = avro.schema.parse(s.read())
        self.numeric_fields = numeric_fields
        self.ignored_fields = ignored_fields
        self.strict = strict

    def timestamp(self, obj) -> int:
        raise NotImplementedError("timestamp method should be implemented in a subclass")
    
    def partition(self, obj) -> str:
        return datetime.fromtimestamp(self.timestamp(obj), tz=timezone.utc).strftime('%Y%m%d')

    def convert(self, obj):
        for field in self.ignored_fields:
            if field in obj:
                del obj[field]
        for field in self.numeric_fields:
            if field not in obj:
                continue
            numeric = obj[field]
            if numeric is not None:
                assert type(numeric) == dict and 'value' in numeric and 'scale' in numeric, f"Wrong format for numeric value: {numeric}"
                obj[field] = int.from_bytes(base64.b64decode(numeric['value']), 'big') / pow(10, numeric['scale'])
        return obj
    
    """
    Name for the table
    """
    def name(self):
        return self.schema.name
