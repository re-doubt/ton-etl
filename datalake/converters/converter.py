import avro.schema

# Base class for all converters. Allows to add postprocessing and extracting additional fields
class Converter:
    def __init__(self, schema_name):
        with open(schema_name, "rb") as s:
            self.schema = avro.schema.parse(s.read())

    def convert(self, obj):
        return obj