from dataclasses import dataclass
from pytoniq_core import Address


@dataclass
class JettonMint:
    __tablename__ = "jetton_mint"
    __schema__ = "parsed"

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    successful: bool
    query_id: int
    amount: int
    minter: str
    from_address: Address
    wallet: str
    owner: str
    response_destination: Address
    forward_ton_amount: int
    forward_payload: bytes
