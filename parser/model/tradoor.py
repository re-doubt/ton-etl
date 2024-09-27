from dataclasses import dataclass
import decimal

@dataclass
class TradoorPerpOrderEvent:
    __tablename__ = 'tradoor_perp_order'

    tx_hash: str
    trace_id: str
    event_time: int
    op_type: int
    token_id: int
    address: str
    is_long: bool
    margin_delta: decimal.Decimal
    size_delta: decimal.Decimal
    trigger_price: decimal.Decimal
    trigger_above: bool
    execution_fee: decimal.Decimal
    order_id: decimal.Decimal
    trx_id: decimal.Decimal
    request_time: int


@dataclass
class TradoorPerpPositionEvent:
    __tablename__ = 'tradoor_perp_position_change'

    tx_hash: str
    trace_id: str
    event_time: int
    is_increased: bool
    trx_id: decimal.Decimal
    order_id: decimal.Decimal
    op_type: int
    position_id: int
    address: str
    token_id: int
    is_long: bool
    margin_delta: decimal.Decimal
    margin_after: decimal.Decimal
    size_delta: decimal.Decimal
    size_after: decimal.Decimal
    trade_price: decimal.Decimal
    entry_price: decimal.Decimal


@dataclass
class TradoorOptionOrderEvent:
    __tablename__ = 'tradoor_option_order'

    tx_hash: str
    trace_id: str
    event_time: int
    address: str
    token_id: int
    client_order_id: decimal.Decimal
    is_call: bool
    order_time: int
    option_interval: int
    strike_price: decimal.Decimal
    option_price: decimal.Decimal
    quantity: decimal.Decimal
    trigger_price: decimal.Decimal
    option_fee: decimal.Decimal
    execution_fee: decimal.Decimal
    is_executed: bool
    order_id: decimal.Decimal
    trx_id: decimal.Decimal
    ts: int
