from loguru import logger
from converters.converter import Converter

class TonFunConverter(Converter):
    def __init__(self):
        super().__init__(
            "schemas/tonfun_bcl_trades.avsc",
            numeric_fields=[
                "ton_amount",
                "bcl_amount",
                "min_receive"
            ],
            ignored_fields=["created", "updated"]
        )
