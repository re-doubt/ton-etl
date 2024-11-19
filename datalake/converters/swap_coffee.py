import base64
from converters.converter import Converter


class SwapCoffeeStakesConverter(Converter):
    def __init__(self):
        super().__init__(
            "schemas/swap_coffee_stakes.avsc",
            numeric_fields=["amount"],
            ignored_fields=["created", "updated"]
        )
