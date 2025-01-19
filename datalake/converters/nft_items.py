import base64
import decimal
from typing import List
from topics import TOPIC_NFT_ITEMS
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter

"""
Generates history entries for nft items
"""
class NFTItemsConverter(Converter):
    def __init__(self):
        super().__init__("schemas/nft_items.avsc", ignored_fields=[], updates_enabled=True)

    def timestamp(self, obj):
        return obj['last_tx_now']
    
    def topics(self) -> List[str]:
        return [TOPIC_NFT_ITEMS]
    
    def convert(self, obj, table_name=None):
        return {
            "address": obj['address'],
            "is_init": obj['init'],
            "index": self.decode_numeric(obj['index']),
            "collection_address": obj['collection_address'],
            "owner_address": obj['owner_address'],
            "content_onchain": obj['content'],
            "timestamp": obj['last_tx_now'],
            "lt": obj['last_transaction_lt']
        }

