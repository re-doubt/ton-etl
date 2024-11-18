import base64
from typing import List
from topics import TOPIC_BLOCKS
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class BlocksConverter(Converter):
    def __init__(self):
        super().__init__("schemas/blocks.avsc")

    def timestamp(self, obj):
        return obj['gen_utime']
    
    def topics(self) -> List[str]:
        return [TOPIC_BLOCKS]
