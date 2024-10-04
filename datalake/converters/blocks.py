import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class BlocksConverter(Converter):
    def __init__(self):
        super().__init__("schemas/blocks.avsc")