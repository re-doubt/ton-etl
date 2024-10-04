import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class TradoorPositionChangeConverter(Converter):
    def __init__(self):
        super().__init__("schemas/tradoor_perp_position_change.avsc", numeric_fields=[
            "trx_id",
            "order_id",
            "position_id",
            "margin_delta",
            "margin_after",
            "size_delta",
            "size_after",
            "trade_price",
            "trigger_price",
            "entry_price",
            "funding_fee",
            "rollover_fee",
            "trading_fee"
            ], ignored_fields=["created", "updated"], strict=False)
