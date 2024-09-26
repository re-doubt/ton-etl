from dataclasses import dataclass
import decimal

@dataclass
class GaspumpEvent:
    __tablename__ = 'gaspump_trade'

    tx_hash: str
    trace_id: str
    event_time: int
    jetton_master: str
    event_type: str # DeployAndBuyEmitEvent, BuyEmitEvent, SellEmitEvent
    trader_address: str # trader
    ton_amount: decimal.Decimal
    jetton_amount: decimal.Decimal
    fee_ton_amount: decimal.Decimal
    input_ton_amount: decimal.Decimal
    bonding_curve_overflow: bool