from loguru import logger

from db import DB
from model.parser import Parser, TOPIC_NFT_TRANSFERS
from model.nft_history import NftHistory
from model.sale_contract import SALE_CONTRACTS


BURN_ADDRESSES = [
    Parser.uf2raw("EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"),
    Parser.uf2raw("EQAREREREREREREREREREREREREREREREREREREREREREeYT"),
]


class NftHistoryParser(Parser):

    def topics(self):
        return [TOPIC_NFT_TRANSFERS]

    def predicate(self, obj) -> bool:
        return True

    def handle_internal(self, obj: dict, db: DB):
        current_owner_code_hash = db.get_account_code_hash(obj.get("old_owner"))
        if not current_owner_code_hash:
            # TODO Add handler for not inited account?
            pass

        new_owner_code_hash = db.get_account_code_hash(obj.get("new_owner"))
        if not new_owner_code_hash and obj.get("new_owner") not in BURN_ADDRESSES:
            # TODO Add handler for not inited account?
            pass

        current_owner_sale = None
        if current_owner_code_hash in SALE_CONTRACTS.keys():
            current_owner_sale = db.get_nft_sale(obj.get("old_owner"))
            if not current_owner_sale:
                # TODO Add handler for not parsed sales
                pass

        new_owner_sale = None
        if new_owner_code_hash in SALE_CONTRACTS.keys():
            new_owner_sale = db.get_nft_sale(obj.get("new_owner"))
            if not new_owner_sale:
                # TODO Add handler for not parsed sales
                new_owner_sale = {}

        current_owner = obj.get("old_owner")
        new_owner = obj.get("new_owner")
        sale_address = None
        code_hash = None
        marketplace = None
        price = None
        is_auction = None

        if new_owner_sale:
            event_type = NftHistory.EVENT_TYPE_INIT_SALE
            sale_address = new_owner_sale.get("address")
            code_hash = new_owner_code_hash
            marketplace = new_owner_sale.get("marketplace")
            current_owner = new_owner_sale.get("owner")
            new_owner = None
            is_auction = new_owner_sale.get("is_auction")
            price = 0 if is_auction else new_owner_sale.get("price")

        elif current_owner_sale and current_owner_sale.get("owner") == obj.get("new_owner"):
            event_type = NftHistory.EVENT_TYPE_CANCEL_SALE
            sale_address = current_owner_sale.get("address")
            code_hash = current_owner_code_hash
            marketplace = current_owner_sale.get("marketplace")
            current_owner = current_owner_sale.get("owner")
            new_owner = None
            is_auction = current_owner_sale.get("is_auction")
            price = 0 if is_auction else current_owner_sale.get("price")

        elif current_owner_sale and current_owner_sale.get("owner") != obj.get("new_owner"):
            event_type = NftHistory.EVENT_TYPE_SALE
            sale_address = current_owner_sale.get("address")
            code_hash = current_owner_code_hash
            marketplace = current_owner_sale.get("marketplace")
            current_owner = current_owner_sale.get("owner")
            is_auction = current_owner_sale.get("is_auction")
            price = current_owner_sale.get("price")

        elif obj.get("new_owner") in BURN_ADDRESSES:
            event_type = NftHistory.EVENT_TYPE_BURN

        else:
            event_type = NftHistory.EVENT_TYPE_TRANSFER

        nft_history = NftHistory(
            tx_hash=obj.get("tx_hash"),
            utime=obj.get("tx_now"),
            tx_lt=obj.get("tx_lt"),
            event_type=event_type,
            nft_item_address=obj.get("nft_item_address"),
            collection_address=obj.get("nft_collection_address"),
            sale_address=sale_address,
            code_hash=code_hash,
            marketplace=marketplace,
            current_owner=current_owner,
            new_owner=new_owner,
            price=price,
            is_auction=is_auction,
        )
        logger.info(f"Adding NFT history event {nft_history}")
        db.serialize(nft_history)
