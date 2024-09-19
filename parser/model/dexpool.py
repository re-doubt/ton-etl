from dataclasses import dataclass
import decimal

"""
CREATE TABLE prices.dex_pools (
	pool varchar NOT null primary KEY,
	platform public.dex_name NULL,
	discovered_at int4 null,
	jetton_left varchar null,
	jetton_right varchar null,
	reserves_left numeric null,
	reserves_right numeric null,
    tvl_usd numeric NULL,
    tvl_ton numeric NULL,
    last_updated int4 null
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
    jetton_left: str
    jetton_right: str
    reserves_left: int
    reserves_right: int
    tvl_usd: decimal.Decimal
    tvl_ton: decimal.Decimal
    last_updated: int

