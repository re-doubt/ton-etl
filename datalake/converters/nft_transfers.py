import base64
from typing import List
from topics import TOPIC_NFT_TRANSFERS
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter


class NFTTransfersConverter(Converter):
    def __init__(self):
        super().__init__("schemas/nft_transfers.avsc", numeric_fields=[
            "query_id",
            "forward_amount"
            ])
        
    def timestamp(self, obj):
        return obj['tx_now']
    
    def topics(self) -> List[str]:
        return [TOPIC_NFT_TRANSFERS]

    def convert(self, obj, table_name=None):
        forward_payload = obj['forward_payload']
        if forward_payload:
            obj['forward_payload'] = base64.b64decode(forward_payload)
            cell = Cell.one_from_boc(base64.b64decode(forward_payload)).begin_parse()
            try:
                obj['comment'] = cell.load_snake_string().replace('\x00', '')
            except Exception as e:
                pass
        # Convert base64 custom_payload into binary
        if obj['custom_payload']:
            obj['custom_payload'] = base64.b64decode(obj['custom_payload'])
        if obj['nft_item_index']:
            obj['nft_item_index'] = str(self.decode_numeric(obj['nft_item_index']))
        return super().convert(obj, table_name)
