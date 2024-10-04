import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class JettonBurnsConverter(Converter):
    def __init__(self):
        super().__init__("schemas/jetton_burns.avsc", numeric_fields=[
            "query_id",
            "amount"
            ])

    def convert(self, obj):
        # Convert base64 custom_payload into binary
        if obj['custom_payload']:
            obj['custom_payload'] = base64.b64decode(obj['custom_payload'])
        return super().convert(obj)