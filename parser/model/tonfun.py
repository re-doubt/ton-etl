from dataclasses import dataclass
import decimal

@dataclass
class TonfunTradeEvent:
    __tablename__ = 'tonfun_trade_event'

    tx_hash: str
    trace_id: str
    event_time: int
    jetton_master: str
    is_buy: bool
    trader_address: str
    ton_amount: decimal.Decimal
    jetton_amount: decimal.Decimal
    new_total_supply: decimal.Decimal
    new_ton_collected: decimal.Decimal

@dataclass
class TonfunSendLiqEvent:
    __tablename__ = 'tonfun_send_liq_event'

    tx_hash: str
    trace_id: str
    event_time: int
    jetton_master: str
    ton_amount: decimal.Decimal
    jetton_amount: decimal.Decimal
