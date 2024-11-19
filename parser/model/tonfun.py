from dataclasses import dataclass
import decimal

@dataclass
class TonFunTradeEvent:
    __tablename__ = 'tonfun_bcl_trade'

    tx_hash: str
    trace_id: str
    event_time: int
    bcl_master: str
    event_type: str  # Buy, Sell
    trader_address: str | None
    ton_amount: decimal.Decimal | None  # Amount in TON
    bcl_amount: decimal.Decimal | None  # Amount of BCL tokens
    min_receive: decimal.Decimal | None  # Minimum amount expected
    referral: str | None  # Referral data
