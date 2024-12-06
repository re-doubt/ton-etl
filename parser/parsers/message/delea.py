from loguru import logger
from pytoniq_core import Cell, Address
import traceback

from db import DB
from model.parser import Parser, TOPIC_MESSAGES
from model.delea import DeleaDeposit, DeleaLiquidation, DeleaWithdraw


DELEA_CONTRACTS = [
    Parser.uf2raw("EQB6rkS8xt3Ey4XugdVqQDe1vt4KJDh813_k2ceoONTCBnyD"),
    Parser.uf2raw("EQCwIIRKpuV9fQpQxdTMhLAO30MNHa6GOYd00TsySOOYtA9n"),
    Parser.uf2raw("EQA2OzCuP8-d_lN2MYxLv5WCNfpLH1NUuugppOZBZgNYn-aa"),
    Parser.uf2raw("EQA6Xba1d30QeSTVW7-cIAq-WHD9ZBFg90dQ7CB8mQ2Cxx25"),
    Parser.uf2raw("EQADnjMkZBCS7-zKAPGHwFXGdd8b85m3bRDm52AX__ORLey-"),
]

DEPOSIT_TON_EVENT = Parser.opcode_signed(0x00bbdf19)
DEPOSIT_JETTON_EVENT = Parser.opcode_signed(0x7362d09c)
WITHDRAW_EVENT = Parser.opcode_signed(0x000a2c32)
LIQUIDATION_EVENT = Parser.opcode_signed(0x000a2c38)


class DeleaDepositParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return (
            obj.get("opcode", None) in [DEPOSIT_JETTON_EVENT, DEPOSIT_TON_EVENT]
            and obj.get("direction", None) == "in"
            and obj.get("destination", None) in DELEA_CONTRACTS
        )

    def handle_internal(self, obj, db: DB):
        logger.info(f"Parsing Delea deposit message {Parser.require(obj.get('msg_hash', None))}")
        cell = Parser.message_body(obj, db).begin_parse()
        deposit_type = cell.load_uint(32)  # 0x11a
        amount = 0
        query_id = 0
        owner_address = Parser.require(obj.get("source", None))
        try:
            if deposit_type == DEPOSIT_TON_EVENT:
                query_id = cell.load_uint(64)
                amount = cell.load_coins()
            elif deposit_type == DEPOSIT_JETTON_EVENT:
                query_id = cell.load_uint(64)
                amount = cell.load_coins()
                owner_address = cell.load_address()
            else :
                logger.info(f"Skipping message with opcode {deposit_type}")
                return
        except Exception as e:
            logger.error(f"Unable to parse deposit event {e}: {traceback.format_exc()}")
            raise Exception(f"Unable to parse deposit event {e}: {traceback.format_exc()}")

        event = DeleaDeposit(
            tx_hash=Parser.require(obj.get("tx_hash", None)),
            msg_hash=Parser.require(obj.get("msg_hash", None)),
            trace_id=Parser.require(obj.get("trace_id", None)),
            utime=Parser.require(obj.get("created_at", None)),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash", None)))),
            query_id=query_id,
            owner_address=owner_address,
            amount=amount,
        )
        logger.info(f"Adding Delea deposit {event}")
        db.serialize(event)


class DeleaWithdrawAndLiquidationParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        return  (
            obj.get("opcode", None) in [WITHDRAW_EVENT, LIQUIDATION_EVENT]
            and obj.get("direction", None) == "in"
            and obj.get("destination", None) in DELEA_CONTRACTS
        )

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        op = cell.load_uint(32)
        event = None
        if op == WITHDRAW_EVENT:
            query_id = cell.load_uint(64)
            amount = cell.load_coins()
            cell.load_coins()
            cell.load_coins()
            cell.load_coins()
            cell.load_uint(64)
            owner_address = cell.load_address()
            sc_1 = cell.load_ref().begin_parse()
            recipient_address = sc_1.load_address()
            event = DeleaWithdraw(
                tx_hash=Parser.require(obj.get("tx_hash", None)),
                msg_hash=Parser.require(obj.get("msg_hash", None)),
                trace_id=Parser.require(obj.get("trace_id", None)),
                utime=Parser.require(obj.get("created_at", None)),
                successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash", None)))),
                query_id=query_id,
                owner_address=owner_address,
                amount=amount,
                recipient_address=recipient_address,
            )
            logger.info(f"Adding Delea withdraw {event}")
        elif op == LIQUIDATION_EVENT:
            query_id = cell.load_uint(64)
            failed = cell.load_bool()
            if failed:
                logger.info(f"Delea liquidation is not successfull {Parser.require(obj.get('msg_hash', None))}")
                return
            amount = cell.load_coins()
            cell.load_coins()
            cell.load_coins()
            cell.load_uint(64)
            if cell.load_bool():
                cell.load_address()
            sc_1 = cell.load_ref().begin_parse()
            liquidator_address = sc_1.loadAddress()
            event = DeleaLiquidation(
                tx_hash=Parser.require(obj.get("tx_hash", None)),
                msg_hash=Parser.require(obj.get("msg_hash", None)),
                trace_id=Parser.require(obj.get("trace_id", None)),
                utime=Parser.require(obj.get("created_at", None)),
                successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash", None)))),
                query_id=query_id,
                owner_address=owner_address,
                amount=amount,
                liquidator_address=liquidator_address,
            )
            logger.info(f"Adding Delea liquidation {event}")
        if event is None :
            logger.error(f"Unable to serialize event {Parser.require(obj.get('msg_hash', None))}: {traceback.format_exc()}")
            raise Exception(f"Unable to serialize event {Parser.require(obj.get('msg_hash', None))}: {traceback.format_exc()}")
        db.serialize(event)
