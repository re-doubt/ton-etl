import base64
from typing import List
import psycopg2
from functools import lru_cache
from topics import TOPIC_MESSAGES
from loguru import logger
from pytoniq_core import Cell
from psycopg2.extras import RealDictCursor
from converters.converter import Converter


class MessageConverter(Converter):
    def __init__(self):
        super().__init__("schemas/messages.avsc", ignored_fields=["body_boc", "init_state_boc"])

    def timestamp(self, obj):
        return obj['tx_now']
    
    def topics(self) -> List[str]:
        return [TOPIC_MESSAGES]

    def convert(self, obj, table_name=None):
        comment = None
        if 'body_boc' in obj:
            cell = Cell.one_from_boc(obj['body_boc']).begin_parse()
            try:
                comment = cell.load_snake_string().replace('\x00', '')
            except Exception as e:
                pass
        obj['comment'] = comment
        return super().convert(obj)
    
class MessageWithDataConverter(Converter):
    def __init__(self):
        super().__init__("schemas/messages_with_data.avsc")

    def timestamp(self, obj):
        return obj['tx_now']
    
    def topics(self) -> List[str]:
        return [TOPIC_MESSAGES]

    def convert(self, obj, table_name=None):
        comment = None
        cell = Cell.one_from_boc(obj['body_boc']).begin_parse()
        obj['body_boc'] = base64.b64decode(obj['body_boc'])
        if obj['init_state_boc']:
            obj['init_state_boc'] = base64.b64decode(obj['init_state_boc'])
        try:
            comment = cell.load_snake_string().replace('\x00', '')
        except Exception as e:
            pass
        obj['comment'] = comment
        return super().convert(obj, table_name)