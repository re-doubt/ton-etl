import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class AggPricesConverter(Converter):
    def __init__(self):
        super().__init__("schemas/agg_prices.avsc", numeric_fields=[
            "price_ton",
            "price_usd"
            ], ignored_fields=["id", "created", "updated"])
