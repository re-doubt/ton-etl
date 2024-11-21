from model.parser import Parser, TOPIC_MESSAGES
from db import DB
from pytoniq_core import Cell, Address
from model.tonfun import TonfunTradeEvent, TonfunSendLiqEvent


"""
Ton.fun jettons emit events for buy, sell, and liquidity deopsit events according to the following TL-B schema:

;;
;; Type: TonfunTradeEvent (buy)
;; Header: 0xcd78325d
;; TLB: buy_event#cd78325d buyer:address ton_amount:coins 
;; jetton_amount:coins new_total_supply:coins new_ton_collected:coins referral:(Maybe ^Cell) = TonfunTradeEvent;
;;
;; Type: TonfunTradeEvent (sell)
;; Header: 0x5e97d116
;; TLB: sell_event#5e97d116 seller:address ton_amount:coins 
;; jetton_amount:coins new_total_supply:coins new_ton_collected:coins referral:(Maybe ^Cell) = TonfunTradeEvent;
;;
;; Type: TonfunSendLiqEvent
;; Header: 0xf6ab54f
;; TLB: send_liq_event#f6ab54f ton_amount:coins jetton_amount:coins = TonfunSendLiqEvent;
;;
"""

BUY_EVENT = Parser.opcode_signed(0xcd78325d)
SELL_EVENT = Parser.opcode_signed(0x5e97d116)
SEND_LIQ_EVENT = Parser.opcode_signed(0xf6ab54f)
EVENTS = [BUY_EVENT, SELL_EVENT, SEND_LIQ_EVENT]

class Tonfun(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only external messages with specific opcodes
        return obj.get("opcode", None) in EVENTS and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", 'None') is None

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        opcode = cell.load_uint(32)
        if opcode == 0xcd78325d or opcode == 0x5e97d116:
            is_buy = opcode == 0xcd78325d
            trader = cell.load_address()
            ton_amount = cell.load_coins()
            jetton_amount = cell.load_coins()
            new_total_supply = cell.load_coins()
            new_ton_collected = cell.load_coins()
            referral = cell.load_maybe_ref()
            event = TonfunTradeEvent(
                tx_hash=Parser.require(obj.get('tx_hash', None)),
                trace_id=Parser.require(obj.get('trace_id', None)),
                event_time=Parser.require(obj.get('created_at', None)),
                jetton_master=Parser.require(obj.get('source', None)),
                is_buy=is_buy,
                trader_address=trader,
                ton_amount=ton_amount,
                jetton_amount=jetton_amount,
                new_total_supply=new_total_supply,
                new_ton_collected=new_ton_collected,
            )
        elif opcode == 0xf6ab54f:
            ton_amount = cell.load_coins()
            jetton_amount = cell.load_coins()
            event = TonfunSendLiqEvent(
                tx_hash=Parser.require(obj.get('tx_hash', None)),
                trace_id=Parser.require(obj.get('trace_id', None)),
                event_time=Parser.require(obj.get('created_at', None)),
                jetton_master=Parser.require(obj.get('source', None)),
                ton_amount=ton_amount,
                jetton_amount=jetton_amount,
            )
        else:
            raise Exception(f"Unsupported opcode: {opcode}")

        db.serialize(event)
