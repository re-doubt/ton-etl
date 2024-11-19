from typing import Optional
from functools import partial
from operator import eq
from decimal import Decimal
from pytoniq_core import Cell
from model.parser import Parser, TOPIC_MESSAGES
from model.tonfun import TonFunTradeEvent
from db import DB

BCL_MASTER = "EQDrB5FAongX_u-eWu7sHPv0knlnxfidzIxn5Q_ZC40loyDa"
is_event = partial(eq, "out").__call__

EVENT_TYPES = {
    0x8e911e50: "buy_log",
    0xc8bd8835: "sell_log",
    0x4a35b2df: "send_liq_log"
}

def parse_referral(cs: Cell) -> dict:
    return {
        "referral": cs.to_string(),
        "partner_address": str(cs.load_address()) if cs.load_bit() else None,
        "platform_tag": str(cs.load_address()) if cs.load_bit() else None,
        "extra_tag": str(cs.load_address()) if cs.load_bit() else None
    }

def parse_event(cs: Cell) -> Optional[dict]:
    event_id = cs.load_uint(32)
    return {
        "buy_log": lambda: {"type": "Buy", **parse_trade_data(cs)},
        "sell_log": lambda: {"type": "Sell", **parse_trade_data(cs)},
        "send_liq_log": lambda: None
    }.get(EVENT_TYPES.get(event_id, "unknown"), lambda: None)()

def parse_trade_data(cs: Cell) -> dict:
    return {
        "trader": cs.load_address(),
        "ton_amount": cs.load_coins(),
        "bcl_amount": cs.load_coins(),
        "current_supply": cs.load_coins(),
        "ton_liq_collected": cs.load_coins(),
        **(parse_referral(cs.load_ref().begin_parse()) if cs.load_bit() else
           {"referral": None, "partner_address": None, "platform_tag": None, "extra_tag": None})
    }

def make_event(obj: dict, trade_data: dict) -> TonFunTradeEvent:
    return TonFunTradeEvent(
        tx_hash=obj["tx_hash"],
        trace_id=obj["trace_id"],
        event_time=obj["created_at"],
        bcl_master=obj["source"],
        event_type=trade_data["type"],
        trader_address=str(trade_data["trader"]),
        ton_amount=to_decimal(trade_data["ton_amount"]),
        bcl_amount=to_decimal(trade_data["bcl_amount"]),
        min_receive=None,
        referral=trade_data["referral"],
        partner_address=trade_data["partner_address"],
        platform_tag=trade_data["platform_tag"],
        extra_tag=trade_data["extra_tag"]
    )

class TonFunTrade(Parser):
    topics = lambda _: [TOPIC_MESSAGES]

    predicate = lambda _, obj: (
        obj.get("opcode") in EVENT_TYPES and
        is_event(obj.get("direction")) and
        obj.get("source", "").startswith(BCL_MASTER)  # Проверяем, что источник - мастер контракт
    )

    def handle_internal(self, obj: dict, db: DB) -> None:
        maybe_trade_data = parse_event(Parser.message_body(obj, db).begin_parse())
        if maybe_trade_data:
            db.serialize(make_event(obj, maybe_trade_data))
