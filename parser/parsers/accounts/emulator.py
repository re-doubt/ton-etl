from model.parser import TOPIC_ACCOUNT_STATES, NonCriticalParserError, Parser
from db import DB
import time
import os
import asyncio
from loguru import logger
from pytvm.tvm_emulator.tvm_emulator import TvmEmulator
from pytvm.engine import EmulatorEngineC
from pytoniq_core import Cell, Address, begin_cell
from pytoniq import LiteClient


"""
Utility class for lazy inittialization of config cell.
Config cell is required for proper emulator initialization.
"""
class ConfigCellHolder:
    def get(self):
        if getattr(self, '_CONFIG_CELL', None) is None:
            logger.info("Initing config cell from the blockchain")
            asyncio.run(self._get_cell())
            logger.info("Config cell initialized")
        return self._CONFIG_CELL
    
    async def _get_cell(self):
        client = LiteClient.from_mainnet_config(  # choose mainnet, testnet or custom config dict
            ls_i=0,  # index of liteserver from config
            trust_level=2,  # trust level to liteserver
            timeout=30  # timeout not includes key blocks synchronization as it works in pytonlib
        )
        await client.connect()
        mc = await client.get_masterchain_info()
        logger.info(f"Got mc info: {mc}")
        cell = await client._get_config_cell(client.last_mc_block)
        self._CONFIG_CELL = cell

CONFIGCELL = ConfigCellHolder()

"""
Any non zero exit codes from the emulator are considered non critical
and are ignored.
"""
class EmulatorException(NonCriticalParserError):
    pass
    
"""
Utility base class for all pytvm backed parsers. Handles 
states and prepares TvmEmulator for the child class.
"""
class EmulatorParser(Parser):
    def __init__(self, emulator_path):
        self.engine = EmulatorEngineC(emulator_path)
        self.engine.emulator_set_verbosity_level(0)

    def topics(self):
        return [TOPIC_ACCOUNT_STATES]
    
    def predicate(self, obj) -> bool:
        return obj.get("data_boc", None) is not None and obj.get("code_boc", None) is not None
    
    def handle_internal(self, obj, db: DB):
        emulator = self._prepare_emulator(obj)
        self._do_parse(obj, db, emulator)

    def _prepare_emulator(self, obj):
        data = Cell.one_from_boc(obj.get('data_boc'))
        code = Cell.one_from_boc(obj.get('code_boc'))
        emulator = TvmEmulator(code, data, verbosity_level=0, engine=self.engine)
        emulator.set_c7(address=obj.get('account'),
                        unixtime=int(time.time()),
                        balance=10, 
                        rand_seed_hex="0443c4e42c6ae4c9e62b584098bc73a699c654130260ae0c4a8a24605921c0be", 
                        config=CONFIGCELL.get())

        return emulator
    
    def _execute_method(self, emulator, method, stack):
        result = emulator.run_get_method(method=method, stack=stack)
        if not result['success']:
            raise EmulatorException(f"Method {method} execution failed: {result}")
        if result['vm_exit_code'] != 0:
            raise EmulatorException(f"Method {method} execution failed with wrong exit code {result['vm_exit_code']}: {result}")
        return result['stack']

    # Actual implementation
    def _do_parse(self, obj, db: DB, emulator: TvmEmulator):
        raise Exception("Not implemented")