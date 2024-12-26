import copy
import time
from typing import Dict
from model.parser import Parser, TOPIC_ACCOUNT_STATES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address, begin_cell, VmTuple, HashMap
from model.dexpool import DexPool
from model.dexswap import DEX_DEDUST, DEX_MEGATON, DEX_STON, DEX_STON_V2, DEX_TONCO
from model.dedust import read_dedust_asset
from parsers.message.swap_volume import estimate_tvl
from pytvm.tvm_emulator.tvm_emulator import TvmEmulator
from parsers.accounts.emulator import EmulatorException, EmulatorParser


"""
Parses staking pools nominators and validators stakes
"""
class StakingPoolsParser(EmulatorParser):
    def __init__(self, emulator_path):
        super().__init__(emulator_path)

    def predicate(self, obj) -> bool:
        # TODO
        return super().predicate(obj)

    def iterate_lisp_list(self, tuple: VmTuple):
        while tuple is not None:
            left, right = tuple.pop(), tuple.pop()
            yield right
            tuple = left

    def _do_parse(self, obj, db: DB, emulator: TvmEmulator):
        OUTPUT_LISP_LIST = 'list_list'
        OUTPUT_DICT = 'dict'
        method_names = [('list_nominators', OUTPUT_LISP_LIST), ('get_members', OUTPUT_LISP_LIST), ('get_members_raw', OUTPUT_DICT)]
        for method, output_type in method_names:
            try:
                res = self._execute_method(emulator, method, [], db, obj)
                logger.info(f"Res for {method}: {res}")
                if len(res) != 1:
                    raise EmulatorException(f"Expected 1 result, got {len(res)}")
                res = res[0]
                if output_type == OUTPUT_LISP_LIST:
                    for item in self.iterate_lisp_list(res):
                        address, balance, pending = item.pop(0), item.pop(0), item.pop(0)
                        if type(address) == int:
                            address = Address((0, address.to_bytes(length=32, byteorder='big')))
                        logger.info(f"Item: {address}, {type(address)}, {balance}, {type(balance)}, {pending}, {type(pending)}")
                        db.insert_staking_position(address, obj['account'], obj['timestamp'], obj['last_trans_lt'], balance, pending)
                elif output_type == OUTPUT_DICT:
                    map = HashMap.parse(res.begin_parse(), key_length=256)
                    logger.info(f"Processing {len(map)} items from hash map")
                    for key, value in map.items():
                        address = Address((0, key.to_bytes(length=32, byteorder='big')))
                        value.load_int(128) # ctx_member_profit_per_coin
                        balance = value.load_coins()
                        pending = value.load_coins()
                        db.insert_staking_position(address, obj['account'], obj['timestamp'], obj['last_trans_lt'], balance, pending)
                break # no need for more attempts
            except EmulatorException as e:
                pass