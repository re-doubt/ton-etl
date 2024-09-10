from dataclasses import dataclass


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
