from dataclasses import dataclass


@dataclass
class SwapCoffeeStake:
    __tablename__ = 'swap_coffee_stake'

    tx_hash: str
    msg_hash: str
    trace_id: str
    utime: int
    vault: str
    user: str
    token: str
    amount: int
    period_id: int
