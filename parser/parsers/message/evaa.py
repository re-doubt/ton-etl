import codecs
from loguru import logger
from pytoniq_core import Cell

from db import DB
from model.parser import Parser, TOPIC_MESSAGES
from model.evaa import EvaaSupply, EvaaWithdraw, EvaaLiquidation


EVAA = Parser.uf2raw("EQC8rUZqR_pWV1BylWUlPNBzyiTYVoBEmQkMIQDZXICfnuRr")


def calc_crc(message):
    poly = 0x1021
    reg = 0
    message += b"\x00\x00"
    for byte in message:
        mask = 0x80
        while mask > 0:
            reg <<= 1
            if byte & mask:
                reg += 1
            mask >>= 1
            if reg > 0xffff:
                reg &= 0xffff
                reg ^= poly
    return reg.to_bytes(2, "big")


def evaa_asset_to_str(asset_id: int):
    addr = b"\x11\x00" + asset_id.to_bytes(32, "big")
    return (
        codecs.decode(codecs.encode(addr + calc_crc(addr), "base64"), "utf-8")
        .strip()
        .replace("/", "_")
        .replace("+", "-")
    )


class EvaaSupplyParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return (
            obj.get("opcode", None) == Parser.opcode_signed(0x11a)
            and obj.get("direction", None) == "in"
            and obj.get("destination", None) == EVAA
        )

    def handle_internal(self, obj, db: DB):
        logger.info(f"Parsing EVAA supply message {Parser.require(obj.get('msg_hash', None))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32)  # 0x11a

        supply = EvaaSupply(
            tx_hash=Parser.require(obj.get("tx_hash", None)),
            msg_hash=Parser.require(obj.get("msg_hash", None)),
            trace_id=Parser.require(obj.get("trace_id", None)),
            utime=Parser.require(obj.get("created_at", None)),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash", None)))),
            query_id=cell.load_uint(64),
            owner_address=cell.load_address(),
            asset_id=evaa_asset_to_str(cell.load_uint(256)),
            amount=cell.load_uint(64),
            repay_amount_principal=cell.load_uint(64),
            supply_amount_principal=cell.load_uint(64),
        )
        logger.info(f"Adding EVAA supply {supply}")
        db.serialize(supply)


class EvaaWithdrawParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return obj.get("direction", None) == "in" and obj.get("source", None) == EVAA

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        try:
            cell.load_coins()  # version
            cell.load_uint(3)  # flags
            op = cell.load_uint(32)
            query_id = cell.load_uint(64)
        except:
            logger.info("Not an EVAA message")
            return

        if op == 0x211a:
            approved = True
        elif op == 0x211f:
            approved = False
        else:
            logger.info(f"Skipping message with opcode {op}")
            return

        logger.info(f"Parsing possible EVAA withdraw approve message {Parser.require(obj.get('msg_hash', None))}")

        parent_message = db.get_parent_message_with_body(obj.get("msg_hash"))
        if not parent_message:
            logger.warning(f"Unable to find parent message for {obj.get('msg_hash')}")
            return

        logger.info(
            f"Parsing EVAA withdraw_collateralized message {Parser.require(parent_message.get('msg_hash', None))}"
        )
        cell = Cell.one_from_boc(Parser.require(parent_message.get("body"))).begin_parse()
        cell.load_uint(32)  # 0x211

        withdraw = EvaaWithdraw(
            tx_hash=Parser.require(parent_message.get("tx_hash", None)),
            msg_hash=Parser.require(parent_message.get("msg_hash", None)),
            trace_id=Parser.require(parent_message.get("trace_id", None)),
            utime=Parser.require(parent_message.get("created_at", None)),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash", None)))),
            query_id=cell.load_uint(64),
            owner_address=cell.load_address(),
            asset_id=evaa_asset_to_str(cell.load_uint(256)),
            amount=cell.load_uint(64),
            borrow_amount_principal=cell.load_uint(64),
            reclaim_amount_principal=cell.load_uint(64),
            approved=approved,
        )
        logger.info(f"Adding EVAA withdraw {withdraw}")
        db.serialize(withdraw)


class EvaaLiquidationParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return obj.get("direction", None) == "in" and obj.get("source", None) == EVAA

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        try:
            cell.load_coins()  # version
            cell.load_uint(3)  # flags
            op = cell.load_uint(32)
            query_id = cell.load_uint(64)
        except:
            logger.info("Not an EVAA message")
            return

        if op == 0x311a:
            approved = True
        elif op == 0x311f:
            approved = False
        else:
            logger.info(f"Skipping message with opcode {op}")
            return

        logger.info(f"Parsing possible EVAA liquidation approve message {Parser.require(obj.get('msg_hash', None))}")

        parent_message = db.get_parent_message_with_body(obj.get("msg_hash"))
        if not parent_message:
            logger.warning(f"Unable to find parent message for {obj.get('msg_hash')}")
            return

        logger.info(f"Parsing EVAA liquidate_satisfied message {Parser.require(parent_message.get('msg_hash', None))}")
        cell = Cell.one_from_boc(Parser.require(parent_message.get("body"))).begin_parse()
        cell.load_uint(32)  # 0x311
        ref = cell.load_ref().begin_parse()

        liqudation = EvaaLiquidation(
            tx_hash=Parser.require(parent_message.get("tx_hash", None)),
            msg_hash=Parser.require(parent_message.get("msg_hash", None)),
            trace_id=Parser.require(parent_message.get("trace_id", None)),
            utime=Parser.require(parent_message.get("created_at", None)),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash", None)))),
            query_id=cell.load_uint(64),
            owner_address=cell.load_address(),
            liquidator_address=cell.load_address(),
            transferred_asset_id=evaa_asset_to_str(cell.load_uint(256)),
            delta_loan_principal=ref.load_int(64),
            amount=ref.load_uint(64),
            protocol_gift=ref.load_uint(64),
            collateral_asset_id=evaa_asset_to_str(ref.load_uint(256)),
            delta_collateral_principal=ref.load_int(64),
            collateral_reward=ref.load_uint(64),
            min_collateral_amount=ref.load_uint(64),
            approved=approved,
        )

        logger.info(f"Adding EVAA liquidation {liqudation}")
        db.serialize(liqudation)
