import time
from typing import Dict
from model.parser import Parser, TOPIC_ACCOUNT_STATES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address, begin_cell
from model.dexpool import DexPool
from model.dexswap import DEX_DEDUST, DEX_STON
from model.dedust import read_dedust_asset
from parsers.message.swap_volume import estimate_tvl
from pytvm.tvm_emulator.tvm_emulator import TvmEmulator
from parsers.accounts.emulator import EmulatorParser


"""
Listens to updates on DEX pools, exrtacts reserves and total_supply
and estimates TVL.
"""
class TVLPoolStateParser(EmulatorParser):
    def __init__(self, emulator_path, update_interval=3600):
        super().__init__(emulator_path)
        self.last_updated = int(time.time())
        # update intervals for pools
        self.update_interval = update_interval
        self.pools: Dict[str, DexPool] = {}

    def prepare(self, db: DB):
        super().prepare(db)
        self.pools = db.get_all_dex_pools()
        logger.info(f"Found {len(self.pools)} unique dex pools to handle")

    def predicate(self, obj) -> bool:
        if super().predicate(obj):
            return obj['account'] in self.pools
        return False
    
    def _do_parse(self, obj, db: DB, emulator: TvmEmulator):
        # TODO refresh pool data every update_interva
        pool = self.pools[obj['account']]
        pool.last_updated = obj['timestamp']

        # total supply is required for all cases
        pool.total_supply, _, _, _, _= self._execute_method(emulator, 'get_jetton_data', [], db, obj)

        if pool.platform == DEX_STON:
            pool.reserves_left, pool.reserves_right, wallet0_address, wallet1_address, _, _, _, _, _, _ = self._execute_method(emulator, 'get_pool_data', [], db, obj)
            # logger.info(f"STON pool data: {pool.reserves_left}, {pool.reserves_right}")
            wallet0_address = wallet0_address.load_address() # jetton wallet address
            wallet1_address = wallet1_address.load_address()

            token0_address = db.get_wallet_master(wallet0_address)
            token1_address = db.get_wallet_master(wallet1_address)
            if token0_address is None:
                logger.warning(f"Jetton wallet {wallet0_address} not found in DB")
                return
            if token1_address is None:
                logger.warning(f"Jetton wallet {wallet1_address} not found in DB")
                return
            current_jetton_left = Address(token0_address)
            current_jetton_right = Address(token1_address)
        elif pool.platform == DEX_DEDUST:
            pool.reserves_left, pool.reserves_right = self._execute_method(emulator, 'get_reserves', [], db, obj)
            logger.info(f"DeDust pool data: {pool.reserves_left}, {pool.reserves_right}")
            if not pool.is_inited():
                wallet0_address, wallet1_address = self._execute_method(emulator, 'get_assets', [], db, obj)
                current_jetton_left = read_dedust_asset(wallet0_address)
                current_jetton_right = read_dedust_asset(wallet1_address)
        else:
            raise Exception(f"DEX is not supported: {pool.platform}")
        
        if not pool.is_inited():
            pool.jetton_left = current_jetton_left
            pool.jetton_right = current_jetton_right
            logger.info(f"Discovered jettons for {pool.pool}: {pool.jetton_left}, {pool.jetton_right}")
            db.update_dex_pool_jettons(pool)
        estimate_tvl(pool, db)
        logger.info(pool)
        db.update_dex_pool_state(pool)
