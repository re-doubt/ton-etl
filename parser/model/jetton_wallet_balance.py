from dataclasses import dataclass


@dataclass
class JettonWalletBalance:
    __tablename__ = "jetton_wallet_balances"
    __schema__ = "parsed"

    id: int
    address: str
    tx_lt: int
    jetton_master: str
    owner: str
    balance: int
