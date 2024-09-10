from dataclasses import dataclass

"""
CREATE TABLE parsed.nft_history (
	tx_hash bpchar(44) not NULL,
    utime int8 NULL,
    tx_lt int8 NULL,
    event_type nft_history_event not NULL,
	nft_item_address varchar NULL,
	collection_address varchar NULL,
	sale_address varchar NULL,
	code_hash varchar NULL,
	marketplace varchar NULL,
	current_owner varchar NULL,
	new_owner varchar NULL,
	price numeric NULL,
    is_auction bool NULL,
	CONSTRAINT nft_history_tx_hash_key PRIMARY KEY (tx_hash)
);
"""

@dataclass
class NftHistory:
    __tablename__ = "nft_history"

    EVENT_TYPE_MINT = "mint"
    EVENT_TYPE_INIT_SALE = "init_sale"
    EVENT_TYPE_CANCEL_SALE = "cancel_sale"
    EVENT_TYPE_SALE = "sale"
    EVENT_TYPE_TRANSFER = "transfer"
    EVENT_TYPE_BURN = "burn"

    tx_hash: str
    utime: int
    tx_lt: int
    event_type: str
    nft_item_address: str
    collection_address: str
    sale_address: str
    code_hash: str
    marketplace: str
    current_owner: str
    new_owner: str
    price: int
    is_auction: bool
