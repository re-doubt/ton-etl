from dataclasses import dataclass


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
    asset_id: str
    owner_address: str
    repay_amount_principal: int
    supply_amount_principal: int


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
    asset_id: str
    owner_address: str
    borrow_amount_principal: int
    reclaim_amount_principal: int
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
    transferred_asset_id: str
    collateral_asset_id: str
    owner_address: str
    liquidator_address: str
    delta_loan_principal: int
    delta_collateral_principal: int
    approved: bool
