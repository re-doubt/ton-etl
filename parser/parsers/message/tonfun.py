from model.parser import Parser, TOPIC_MESSAGES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address
from model.tonfun import TonFunTradeEvent

BCL_MASTER_ADDRESS = "EQDrB5FAongX_u-eWu7sHPv0knlnxfidzIxn5Q_ZC40loyDa"

BUY_EVENT = Parser.opcode_signed(0xAF750D34)
SELL_EVENT = Parser.opcode_signed(0x742B36D8)
EVENTS = [BUY_EVENT, SELL_EVENT]

class TonFunTrade(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return obj.get("opcode", None) in EVENTS and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", 'None') is None

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        opcode = cell.load_uint(32)
        query_id = cell.load_uint(64)

        if opcode == BUY_EVENT:
            event_type = "Buy"
            min_receive = cell.load_coins()
            referral = cell.load_maybe_ref()
            trader_address = cell.load_address() if cell.has_bits() else None
            ton_amount = obj.get('value', 0)
            bcl_amount = min_receive

        elif opcode == SELL_EVENT:
            event_type = "Sell"
            bcl_amount = cell.load_coins()
            min_receive = cell.load_coins()
            referral = cell.load_maybe_ref()
            trader_address = obj.get('source', None)
            ton_amount = min_receive

        event = TonFunTradeEvent(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            event_time=Parser.require(obj.get('created_at', None)),
            bcl_master=BCL_MASTER_ADDRESS,
            event_type=event_type,
            trader_address=str(trader_address) if trader_address else None,
            ton_amount=float(ton_amount) / 1e9 if ton_amount else None,
            bcl_amount=float(bcl_amount) / 1e9 if bcl_amount else None,
            min_receive=float(min_receive) / 1e9 if min_receive else None,
            referral=str(referral) if referral else None
        )

        db.serialize(event)
