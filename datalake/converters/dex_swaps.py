import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class DexSwapsConverter(Converter):
    def __init__(self):
        super().__init__("schemas/dex_swaps.avsc", numeric_fields=[
            "swap_src_amount",
            "swap_dst_amount",
            "reserve0",
            "reserve1",
            "query_id",
            "min_out",
            "volume_usd",
            "volume_ton"
            ], ignored_fields=["created", "updated", "id"])
