from model.parser import Parser, TOPIC_MESSAGES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address
from model.tradoor import TradoorOptionOrderEvent, TradoorPerpOrderEvent, TradoorPerpPositionEvent
from parsers.message.swap_volume import estimate_volume


TRADOOR_MAIN_VAULT = '0:FF1338C9F6ED1FA4C264A19052BFF64D10C8AD028628F52B2E0F4B357A12227E'

class TradoorPerpOrder(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only external messages not blacklist
        return obj.get("opcode", None) == Parser.opcode_signed(0xad8e31ef) and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", 'None') is None and \
            obj.get("source", None) == TRADOOR_MAIN_VAULT

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0xad8e31ef
        event = TradoorPerpOrderEvent(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            event_time=Parser.require(obj.get('created_at', None)),
            op_type=cell.load_uint(8),
            token_id=cell.load_uint(16),
            address=cell.load_address(),
            is_long=cell.load_uint(1) == 1,
            margin_delta=cell.load_coins(),
            size_delta=cell.load_coins(),
            trigger_price=cell.load_uint(128),
            trigger_above=cell.load_uint(1) == 1,
            execution_fee=cell.load_coins(),
            order_id=cell.load_uint(64),
            trx_id=cell.load_uint(64),
            request_time=cell.load_uint(32),
        )

        db.serialize(event)

class TradoorPerpPositionChange(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only external messages not blacklist
        return obj.get("opcode", None) == Parser.opcode_signed(0x47596abe) and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", 'None') is None and \
            obj.get("source", None) == TRADOOR_MAIN_VAULT

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0x47596abe
        ref = cell.load_ref().begin_parse()
        event = TradoorPerpPositionEvent(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            event_time=Parser.require(obj.get('created_at', None)),
            trx_id=cell.load_uint(64),
            order_id=cell.load_uint(64),
            op_type=cell.load_uint(8),
            position_id=cell.load_uint(64),
            address=cell.load_address(),
            token_id=cell.load_uint(16),            
            is_long=cell.load_uint(1) == 1,
            margin_delta=cell.load_uint(128),
            margin_after=cell.load_coins(),
            size_delta=cell.load_uint(128),
            size_after=cell.load_coins(),
            trade_price=ref.load_uint(128),
            entry_price=ref.load_uint(128),
            funding_fee=ref.load_uint(128),
            rollover_fee=ref.load_coins(),
            trading_fee=ref.load_coins()
        )

        db.serialize(event)

TRADOOR_OPTION_VAULT = '0:2F5744A4A075330D5E8BE9E96A5904BA387612FA5FDB4134EACAC7E7AB6497F1'

class TradoorOptionOrder(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only external messages not blacklist
        return obj.get("opcode", None) == Parser.opcode_signed(0x3d135687) and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", 'None') is None and \
            obj.get("source", None) == TRADOOR_OPTION_VAULT

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0x3d135687
        ref = cell.load_ref().begin_parse()
        event = TradoorOptionOrderEvent(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            event_time=Parser.require(obj.get('created_at', None)),
            address=cell.load_address(),
            token_id=cell.load_uint(64),
            client_order_id=cell.load_uint(64),
            is_call=cell.load_uint(1) == 1,
            order_time=cell.load_uint(32),
            option_interval=cell.load_uint(32),
            strike_price=cell.load_uint(128),
            option_price=cell.load_uint(128),
            quantity=cell.load_uint(128),
            trigger_price=cell.load_uint(128),
            option_fee=ref.load_uint(128),
            execution_fee=ref.load_coins(),
            is_executed=ref.load_uint(1) == 1,
            order_id=ref.load_uint(64),
            trx_id=ref.load_uint(64),
            ts=ref.load_uint(32),
        )
        db.serialize(event)