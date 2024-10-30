import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class AccountStatesConverter(Converter):
    def __init__(self):
        super().__init__("schemas/account_states.avsc", ignored_fields=["id", "account_friendly"])

    def timestamp(self, obj):
        return obj['timestamp']
    
    def convert(self, obj):
        if obj['data_boc']:
            obj['data_boc'] = base64.b64decode(obj['data_boc'])
        if obj['code_boc']:
            obj['code_boc'] = base64.b64decode(obj['code_boc'])

        return super().convert(obj)            
