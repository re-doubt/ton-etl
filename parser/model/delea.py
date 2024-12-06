from dataclasses import dataclass
from pytoniq_core import Address


@dataclass
class DeleaDeposit:
    __tablename__ = "delea_deposit"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int  # amount_supplied
    owner_address: Address


@dataclass
class DeleaWithdraw:
    __tablename__ = "delea_withdraw"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int  # withdraw_amount_current
    owner_address: Address
    recipient_address: Address


@dataclass
class DeleaLiquidation:
    __tablename__ = "delea_liquidation"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int  # liquidatable_amount
    owner_address: Address
    liquidator_address: Address

