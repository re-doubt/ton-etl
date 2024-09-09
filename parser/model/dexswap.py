from dataclasses import dataclass
import decimal

@dataclass
class DexSwapParsed:
    __tablename__ = 'dex_swap_parsed'

    tx_hash: str
    msg_hash: str
    trace_id: str
    platform: str
    swap_utime: int
    swap_user: str
    swap_pool: str
    swap_src_token: str
    swap_dst_token: str
    swap_src_amount: decimal.Decimal
    swap_dst_amount: decimal.Decimal
    referral_address: str
