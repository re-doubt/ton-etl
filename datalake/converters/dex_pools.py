import base64
from dataclasses import dataclass, asdict
import decimal
from typing import List
from converters.dex_trades import DEX_MAPPING, DEX_VERSION_MAPPING
from topics import TOPIC_DEX_POOLS
from loguru import logger
from converters.converter import Converter

"""
DEX Pools history data model
"""

class DexPoolsConverter(Converter):
    def __init__(self):
        super().__init__("schemas/dex_pools.avsc", ignored_fields=[], updates_enabled=True,
                         numeric_fields=["reserves_left", "reserves_right", "total_supply"])

    def timestamp(self, obj):
        return obj['last_updated'] or 0
        
    def topics(self) -> List[str]:
        return [TOPIC_DEX_POOLS]

    def convert(self, obj, table_name=None):
        if obj['last_updated'] is None:
            logger.warning(f"DEX pool {obj} has no last_updated field")
            return
        obj['project'] = DEX_MAPPING.get(obj['platform'], obj['platform'])
        obj['version'] = DEX_VERSION_MAPPING.get(obj['platform'], 1) # default version - 1
        del obj['platform']
        
        for fee_field in ['lp_fee', 'protocol_fee', 'referral_fee']:
            if obj[fee_field] is not None:
                obj[fee_field] = round(decimal.Decimal(self.decode_numeric(obj[fee_field])), 10)

        if obj['tvl_usd'] is not None:
            obj['tvl_usd'] = round(decimal.Decimal(self.decode_numeric(obj['tvl_usd'])), 6)
        if obj['tvl_ton'] is not None:
            obj['tvl_ton'] = round(decimal.Decimal(self.decode_numeric(obj['tvl_ton'])), 9)
        return super().convert(obj, table_name)
