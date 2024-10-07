from dataclasses import dataclass
from pytoniq_core import Address


@dataclass
class StormExecuteOrder:
    __tablename__ = "storm_execute_order"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool

    direction: int
    order_index: int
    trader_addr: Address
    prev_addr: Address
    ref_addr: Address
    executor_index: int
    order_type: int
    expiration: int
    direction_order: int
    amount: int
    triger_price: int
    leverage: int
    limit_price: int
    stop_price: int
    stop_triger_price: int
    take_triger_price: int
    position_size: int
    direction_position: int
    margin: int
    open_notional: int
    last_updated_cumulative_premium: int
    fee: int
    discount: int
    rebate: int
    last_updated_timestamp: int
    oracle_price: int
    spread: int
    oracle_timestamp: int
    asset_id: int


@dataclass
class StormCompleteOrder:
    __tablename__ = "storm_complete_order"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool

    order_type: int
    order_index: int
    direction: int
    origin_op: int
    oracle_price: int
    position_size: int
    direction_position: int
    margin: int
    open_notional: int
    last_updated_cumulative_premium: int
    fee: int
    discount: int
    rebate: int
    last_updated_timestamp: int
    quote_asset_reserve: int
    quote_asset_weight: int
    base_asset_reserve: int


@dataclass
class StormUpdatePosition:
    __tablename__ = "storm_update_position"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool

    direction: int
    origin_op: int
    oracle_price: int
    stop_trigger_price: int
    take_trigger_price: int
    position_size: int
    direction_position: int
    margin: int
    open_notional: int
    last_updated_cumulative_premium: int
    fee: int
    discount: int
    rebate: int
    last_updated_timestamp: int
    quote_asset_reserve: int
    quote_asset_weight: int
    base_asset_reserve: int


@dataclass
class StormTradeNotification:
    __tablename__ = "storm_trade_notification"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool

    asset_id: int
    free_amount: int
    locked_amount: int
    exchange_amount: int
    withdraw_locked_amount: int
    fee_to_stakers: int
    withdraw_amount: int
    trader_addr: Address
    origin_addr: Address
    referral_amount: int
    referral_addr: Address
