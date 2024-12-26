import copy
import time
from typing import Dict
from model.parser import Parser, TOPIC_ACCOUNT_STATES
from loguru import logger
from db import DB
from pytoniq_core import Address, VmTuple, HashMap, Slice
from pytvm.tvm_emulator.tvm_emulator import TvmEmulator
from parsers.accounts.emulator import EmulatorException, EmulatorParser


"""
Parses staking pools nominators and validators stakes
We will try to invoke multiple methods to get list of nominators.
If none of them works the code_hash will be blacklisted to avoid further attempts.
"""
class StakingPoolsParser(EmulatorParser):
    def __init__(self, emulator_path):
        super().__init__(emulator_path)
        self.blacklist = set()

    def predicate(self, obj) -> bool:
        return super().predicate(obj) and obj['code_hash'] not in self.blacklist

    def iterate_lisp_list(self, tuple: VmTuple):
        while tuple is not None:
            left, right = tuple.pop(), tuple.pop()
            yield right
            tuple = left

    def _do_parse(self, obj, db: DB, emulator: TvmEmulator):
        OUTPUT_LISP_LIST = 'list_list'
        OUTPUT_DICT = 'dict'
        method_names = [('list_nominators', OUTPUT_LISP_LIST), ('get_members', OUTPUT_LISP_LIST), ('get_members_raw', OUTPUT_DICT)]
        handled = False
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
                        elif type(address) == Slice:
                            address = address.load_address()
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
                handled = True
                break # no need for more attempts
            except EmulatorException as e:
                pass
        if not handled:
            self.blacklist.add(obj['code_hash'])
