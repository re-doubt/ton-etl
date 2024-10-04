import base64
import avro.schema

"""
Base class for all converters. Allows to add postprocessing and extracting additional fields.
Also includes list of numeric fields which should be converted to double instead of 
{scale:, value:} json notation by debezium.
"""
class Converter:
    def __init__(self, schema_name, numeric_fields=[]):
        with open(schema_name, "rb") as s:
            self.schema = avro.schema.parse(s.read())
        self.numeric_fields = numeric_fields

    def convert(self, obj):
        for field in self.numeric_fields:
            numeric = obj[field]
            assert type(numeric) == dict and 'value' in numeric and 'scale' in numeric, f"Wrong format for numeric value: {numeric}"
            obj[field] = int.from_bytes(base64.b64decode(numeric['value']), 'big') / pow(10, numeric['scale'])
        return obj
    
    """
    Name for the table
    """
    def name(self):
        return self.schema.name
