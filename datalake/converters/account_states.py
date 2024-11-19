import base64
from typing import List
from topics import TOPIC_ACCOUNT_STATES
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class AccountStatesConverter(Converter):
    def __init__(self):
        super().__init__("schemas/account_states.avsc", ignored_fields=["id", "account_friendly"], updates_enabled=True)

    def timestamp(self, obj):
        return obj['timestamp']
    
    def topics(self) -> List[str]:
        return [TOPIC_ACCOUNT_STATES]
    
    def convert(self, obj, table_name=None):
        if obj['data_boc']:
            obj['data_boc'] = base64.b64decode(obj['data_boc'])
        if obj['code_boc']:
            obj['code_boc'] = base64.b64decode(obj['code_boc'])

        return super().convert(obj, table_name)            
