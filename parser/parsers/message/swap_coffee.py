from model.parser import Parser, TOPIC_MESSAGES
from db import DB
from model.swap_coffee import SwapCoffeeStake

SWAP_COFFEE_STAKING_VAULT = Parser.uf2raw('EQAp-QUzk31pYQWIO5gelCfRrkEe71sI6rg_SvicSV0n31rf')


class SwapCoffeeStakeParser(Parser):

    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return obj.get("opcode", None) == Parser.opcode_signed(0xf9471134) and \
            obj.get("direction", None) == "in" and \
            obj.get("source", None) == SWAP_COFFEE_STAKING_VAULT

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        opcode = cell.load_uint(32)
        query_id = cell.load_uint(64)
        jetton_wallet = cell.load_address()
        jetton_amount = cell.load_coins()
        user_wallet = cell.load_address()
        period_id = cell.load_uint(32)
        event = SwapCoffeeStake(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            msg_hash=Parser.require(obj.get('msg_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            utime=Parser.require(obj.get('created_at', None)),
            vault=Parser.require(obj.get('source', None)),
            user=user_wallet,
            token=jetton_wallet,
            amount=jetton_amount,
            period_id=period_id
        )
        db.serialize(event)
