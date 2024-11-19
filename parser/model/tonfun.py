from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class TonFunTradeEvent:
    __tablename__ = 'tonfun_bcl_trade'
    tx_hash: str
    trace_id: str
    event_time: int
    bcl_master: str
    event_type: str  # Buy, Sell
    trader_address: Optional[str]
    ton_amount: Decimal
    bcl_amount: Decimal
    min_receive: Decimal
    referral: Optional[str]  # Referral data
    # TL-B: ref_v1$_ partner:MaybeAddress platformTag:MaybeAddress extraTag:MaybeAddress = ReferralConfig;
    partner_address: Optional[str]  # partner field of referral slice
    platform_tag: Optional[str]     # platformTag field of referral slice
    extra_tag: Optional[str]        # extraTag field of referral slice
