import base64
import decimal
from typing import List
from topics import TOPIC_ACCOUNT_STATES, TOPIC_JETTON_WALLETS
from loguru import logger
from pytoniq_core import Cell
from converters.converter import Converter

ASSET_TON = "TON"

"""
Generates balances history for native TON balances and Jetton balances
"""
class BalancesHistoryConverter(Converter):
    def __init__(self):
        super().__init__("schemas/balances_history.avsc", ignored_fields=[], updates_enabled=True)

    def timestamp(self, obj):
        if obj['__table'] == "jetton_wallets":
            return obj['last_tx_now']
        else:
            return obj['timestamp']
    
    def topics(self) -> List[str]:
        return [TOPIC_ACCOUNT_STATES, TOPIC_JETTON_WALLETS]
    
    def convert(self, obj, table_name=None):
        if obj['__table'] == "jetton_wallets":
            return {
                "address": obj['owner'],
                "asset": obj['jetton'],
                "amount": self.decode_numeric(obj['balance']),
                "timestamp": obj['last_tx_now'],
                "lt": obj['last_tx_lt']
            }
        else: # account_states
            return {
                "address": obj['account'],
                "asset": ASSET_TON,
                "amount": decimal.Decimal(obj['balance']),
                "timestamp": obj['timestamp'],
                "lt": obj['last_trans_lt']
            }
