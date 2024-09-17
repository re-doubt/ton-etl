from dataclasses import dataclass
import decimal

"""
Almost the same as dexswaps, but with base and quote asset

CREATE TABLE parsed.dex_trade (
	tx_hash bpchar(44) not null primary key,
	platform public.dex_name NULL,
	swap_utime int8 NULL,
	swap_pool varchar NULL,
	base varchar NULL,
	quote varchar NULL,
    base_amount numeric NULL,
    quote_amount numeric NULL,
    price numeric NULL,
	price_ton numeric NULL,
    price_usd numeric NULL,
    volume_ton numeric NULL,
    volume_usd numeric NULL,
    created timestamp NULL,
	updated timestamp NULL
);

create index dex_trade_last_trades on parsed.dex_trade(base, swap_utime)
"""

@dataclass
class DexTrade:
    __tablename__ = 'dex_trade'
    __schema__ = 'prices'

    tx_hash: str
    platform: str
    swap_utime: int
    swap_pool: str
    base: str
    quote: str
    base_amount: decimal.Decimal
    quote_amount: decimal.Decimal
    price: decimal.Decimal = None
    price_ton: decimal.Decimal = None
    price_usd: decimal.Decimal = None
    volume_usd: decimal.Decimal = None
    volume_ton: decimal.Decimal = None
