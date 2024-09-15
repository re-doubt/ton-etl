from model.parser import Parser, TOPIC_ACCOUNT_STATES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address, begin_cell
from pytvm.tvm_emulator.tvm_emulator import TvmEmulator
from parsers.accounts.emulator import EmulatorParser


"""
Goes through all NFTs in states and push it to the nft_items table.
This is special parser that is required if you indexed chain not from the first block
but used ton-smc-scanner to extract all states for some mc seqno and you need to populate
all NFTs as well
"""
class NFTsRecover(EmulatorParser):
    def __init__(self, emulator_path):
        super().__init__(emulator_path)
    
    def _do_parse(self, obj, db: DB, emulator: TvmEmulator):
        nft_address = Address(obj['account'])

        init, index, collection_address, \
            owner_address, individual_content = self._execute_method(emulator, 'get_nft_data', [])
        
        collection_address = collection_address.load_address()
        owner_address = owner_address.load_address()
        # Check that NFT address is not faked, i.e. collection returns the same address for its index
        if collection_address is not None:
            collection_state = db.get_latest_account_state(collection_address)
            collection_emulator = self._prepare_emulator(collection_state)
            
            original_address, = self._execute_method(collection_emulator, 'get_nft_address_by_index', [index])
            original_address = original_address.load_address()
            if original_address != nft_address:
                logger.warning(f"NFT address mismatch: {original_address} != {nft_address}")
                return

        # Ignore contnet at this method, because it requires one more get method invocation
        db.insert_nft_item(nft_address, index, collection_address, owner_address, obj['last_trans_lt'],
                           obj['code_hash'], obj['data_hash'])
