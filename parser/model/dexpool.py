from dataclasses import dataclass
import decimal
from pytoniq_core import Address

"""
CREATE TABLE prices.dex_pool (
	pool varchar NOT null primary KEY,
	platform public.dex_name NULL,
	discovered_at int4 null,
	jetton_left varchar null,
	jetton_right varchar null,
	reserves_left numeric null,
	reserves_right numeric null,
    total_supply numeric null,
    tvl_usd numeric NULL,
    tvl_ton numeric NULL,
    last_updated int4 null,
    is_liquid boolean null
);

CREATE TABLE prices.dex_pool_history (
	pool varchar NOT null,
    timestamp int4 null,
	reserves_left numeric null,
	reserves_right numeric null,
    total_supply numeric null,
    tvl_usd numeric NULL,
    tvl_ton numeric NULL,
    PRIMARY KEY (pool, timestamp)
);

CREATE TABLE prices.dex_pool_link (
    id serial primary key,
    jetton varchar null,
    pool varchar null references prices.dex_pools(pool)
);
create index  dex_pool_link_jetton on  prices.dex_pool_link (jetton)

"""
@dataclass
class DexPool:
    __tablename__ = 'dex_pool'
    __schema__ = 'prices'

    pool: str
    platform: str
    jetton_left: Address
    jetton_right: Address
    reserves_left: int = None
    reserves_right: int = None
    total_supply: int = None
    tvl_usd: decimal.Decimal = None
    tvl_ton: decimal.Decimal = None
    last_updated: int = None
    is_liquid: bool = True # True if the pool contains TON, LSD or stable coin

    def is_inited(self):
        return self.jetton_left is not None and self.jetton_right is not None

