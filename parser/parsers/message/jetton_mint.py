from loguru import logger
from pytoniq_core import Cell, Address

from db import DB
from model.parser import Parser, TOPIC_MESSAGES
from model.jetton_mint import JettonMint


"""
TEP-74 jetton standard does not specify mint format but it has recommended form of internal_transfer message:

internal_transfer  query_id:uint64 amount:(VarUInteger 16) from:MsgAddress
                     response_address:MsgAddress
                     forward_ton_amount:(VarUInteger 16)
                     forward_payload:(Either Cell ^Cell)
                     = InternalMsgBody;

So mint is an internal_transfer without preceding transfer message
"""
class JettonMintParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj: dict) -> bool:
        return obj.get("opcode") == Parser.opcode_signed(0x178d4519) and obj.get("direction") == "in"

    def handle_internal(self, obj: dict, db: DB):
        # ensure we have no transfer operation before
        prev_message = db.get_parent_message_with_body(obj.get("msg_hash"))
        if prev_message and prev_message.get("opcode") == Parser.opcode_signed(0x0f8a7ea5):
            # skip ordinary chain transfer => internal_transfer
            return
        logger.info(f"Parsing jetton mint message {Parser.require(obj.get('msg_hash'))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # internal_transfer#0x178d4519
        query_id = cell.load_uint(64)
        amount = cell.load_coins()
        from_address = cell.load_address()
        response_destination = cell.load_address()
        forward_ton_amount = cell.load_coins()

        forward_payload = None
        try:
            if cell.load_uint(1):
                forward_payload = cell.load_ref()
            else:
                # in-place, read the rest of the cell slice and refs
                forward_payload = cell.to_cell()
        except Exception as e:
            logger.error(f"Unable to parse forward payload {e}")

        mint = JettonMint(
            tx_hash=Parser.require(obj.get("tx_hash")),
            msg_hash=Parser.require(obj.get("msg_hash")),
            trace_id=Parser.require(obj.get("trace_id")),
            utime=Parser.require(obj.get("created_at")),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash")))),
            query_id=query_id,
            amount=amount,
            minter=Parser.require(obj.get("source")),
            wallet=Parser.require(obj.get("destination")),
            from_address=from_address,
            response_destination=response_destination,
            forward_ton_amount=forward_ton_amount,
            forward_payload=forward_payload.to_boc(True, True) if forward_payload is not None else None,
        )
        logger.info(f"Adding jetton mint {mint}")
        db.serialize(mint)
