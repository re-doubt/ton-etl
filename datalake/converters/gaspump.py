import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class GasPumpConverter(Converter):
    def __init__(self):
        super().__init__("schemas/gaspump_trades.avsc", numeric_fields=[
            "ton_amount",
            "jetton_amount",
            "fee_ton_amount",
            "input_ton_amount"
            ], ignored_fields=["created", "updated"])
