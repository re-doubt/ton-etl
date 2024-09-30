from loguru import logger

from db import DB
from model.parser import Parser, TOPIC_JETTON_WALLETS
from model.jetton_wallet_balance import JettonWalletBalance


class JettonWalletBalancesParser(Parser):

    def topics(self):
        return [TOPIC_JETTON_WALLETS]

    def predicate(self, obj) -> bool:
        return True

    def handle_internal(self, obj: dict, db: DB):
        balance = JettonWalletBalance(
            tx_hash=Parser.require(obj.get("tx_hash", None)),
            address=obj.get("address", None),
            tx_lt=obj.get("last_transaction_lt", None),
            jetton_master=obj.get("jetton", None),
            owner=obj.get("owner", None),
            balance=obj.get("balance", None)
        )
        logger.info(f"Adding jetton wallet balance {balance}")
        db.serialize(balance)
