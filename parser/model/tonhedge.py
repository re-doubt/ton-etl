from dataclasses import dataclass
import decimal

@dataclass
class TonHedgeOptionPurchasedEvent:
    __tablename__ = 'tonhedge_option'

    tx_hash: str
    trace_id: str
    event_time: int
    option_type: str
    option_price: decimal.Decimal
    opened_asset_price: decimal.Decimal
    strike_price: decimal.Decimal
    period: int
    amount: int
    purchased_at: int
    id: int
    initial_holder: str
    service_fee: decimal.Decimal
    premium: decimal.Decimal
    notional_volume: decimal.Decimal
    volume: decimal.Decimal
