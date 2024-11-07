import base64
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter, NumericField


"""
The converter is designed to handle events from jetton_mint, jetton_burn and jetton_transfers tables.
"""
class JettonEventsConverter(Converter):
    def __init__(self):
        super().__init__("schemas/jetton_events.avsc", numeric_fields=[
            NumericField(name="query_id", is_integer=True, as_string=True),
            NumericField(name="forward_ton_amount", is_integer=True, as_string=True),
            NumericField(name="amount", is_integer=True, as_string=True),
            ])
        
    def timestamp(self, obj):
        if obj['__table'] == "jetton_mint":
            return obj['utime']
        else:
            return obj['tx_now']

    def convert(self, obj, table_name=None):
        if table_name == "jetton_mint":
            obj['type'] = "mint"
            obj['tx_aborted'] = not obj['successful']
            del obj['successful']
            obj['jetton_wallet'] = obj['wallet']
            del obj['wallet']
            del obj['minter']
        elif table_name == "jetton_burn":
            obj['type'] = "burn"
            obj['utime'] = obj['tx_now']
            del obj['tx_now']
            obj['source'] = obj['owner']
            obj['destination'] = None
            obj['jetton_wallet'] = obj['jetton_wallet_address']
            del obj['jetton_wallet_address']
        elif table_name == "jetton_transfers":
            obj['type'] = "transfer"
            obj['utime'] = obj['tx_now']
            del obj['tx_now']
            obj['jetton_wallet'] = obj['jetton_wallet_address']
            del obj['jetton_wallet_address']

        obj['jetton_master'] = obj['jetton_master_address']
        del obj['jetton_master_address']

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
        return super().convert(obj, table_name)