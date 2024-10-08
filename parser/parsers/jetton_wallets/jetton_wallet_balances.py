from loguru import logger

from db import DB
from model.parser import Parser, TOPIC_JETTON_WALLETS
from model.jetton_wallet_balance import JettonWalletBalance
from parsers.utils import decode_decimal


class JettonWalletBalancesParser(Parser):

    def topics(self):
        return [TOPIC_JETTON_WALLETS]

    def predicate(self, obj) -> bool:
        return True

    def handle_internal(self, obj: dict, db: DB):
        balance = JettonWalletBalance(
            address=obj.get("address", None),
            tx_lt=obj.get("last_transaction_lt", None),
            jetton_master=obj.get("jetton", None),
            owner=obj.get("owner", None),
            balance=decode_decimal(obj.get("balance", None))
        )
        logger.info(f"Adding jetton wallet balance {balance}")
        db.serialize(balance)
