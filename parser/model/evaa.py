from dataclasses import dataclass
from pytoniq_core import Address


@dataclass
class EvaaSupply:
    __tablename__ = "evaa_supply"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int  # amount_supplied
    asset_id: Address
    owner_address: Address
    user_new_principal: int
    repay_amount_principal: int
    supply_amount_principal: int
    pool_address: str


@dataclass
class EvaaWithdraw:
    __tablename__ = "evaa_withdraw"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int  # withdraw_amount_current
    asset_id: Address
    owner_address: Address
    user_new_principal: int
    borrow_amount_principal: int
    reclaim_amount_principal: int
    recipient_address: Address
    pool_address: str
    approved: bool


@dataclass
class EvaaLiquidation:
    __tablename__ = "evaa_liquidation"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int  # liquidatable_amount
    protocol_gift: int
    collateral_reward: int
    min_collateral_amount: int
    transferred_asset_id: Address
    collateral_asset_id: Address
    owner_address: Address
    liquidator_address: Address
    delta_loan_principal: int
    delta_collateral_principal: int
    new_user_loan_principal: int
    new_user_collateral_principal: int
    pool_address: str
    approved: bool
