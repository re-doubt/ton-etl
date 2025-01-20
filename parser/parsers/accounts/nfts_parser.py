import base64
import hashlib
import traceback
from model.parser import Parser, TOPIC_ACCOUNT_STATES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address, begin_cell, HashMap, Builder
from pytvm.tvm_emulator.tvm_emulator import TvmEmulator
from parsers.accounts.emulator import EmulatorException, EmulatorParser

TON_DNS = Address('0:B774D95EB20543F186C06B371AB88AD704F7E256130CAF96189368A7D0CB6CCF')
KEY_DOMAIN = 'domain'
KEY_URI = 'uri'
KEYS = [(int(hashlib.sha256(k.encode()).hexdigest(), 16), k) for k in [KEY_URI, "name", "description", "image", "image_url", "image_data", "symbol", "content_url", "attributes"]]

"""
TODO: nft_items from ton-index-worker has some missing cases for metadata and also
there is a bug in datalake version that generates wrong timestamps
"""
class NFTItemsParser(EmulatorParser):
    def __init__(self, emulator_path):
        super().__init__(emulator_path)
        self.code_hash_blacklist = set()
        self.collections_emulators = {}

    def prepare(self, db: DB):
        super().prepare(db)

    def predicate(self, obj) -> bool:
        if super().predicate(obj):
            return obj['code_hash'] not in self.code_hash_blacklist
        return False
    
    def parse_metadata(self, content_cell: Cell):
        def value_deserializer(value_cs):
            logger.info(f"value_cs: {value_cs.remaining_bits} {value_cs.refs}")
            if value_cs.remaining_bits >= 8:
                kind = value_cs.load_uint(8)
                if kind == 0: # snake format
                    return value_cs.load_snake_string()
                elif kind == 1: # chunked
                    chunks = value_cs.load_dict(key_length=32, value_deserializer=lambda x: x.load_snake_string())
                    out = ""
                    idx = 0
                    while idx in chunks:
                        out += chunks[idx]
                        idx += 1
                    return out
                else:
                    raise Exception(f"Unknown metadata value kind: {kind}")
            else:
                if len(value_cs.refs) > 0:
                    return value_deserializer(value_cs.refs[0].begin_parse())
                return None
            

        content = content_cell.begin_parse()
        logger.info(f"{base64.b64encode(content_cell.to_boc()).decode()}")
        try:
            marker = content.load_uint(8)
        except Exception as e:
            logger.warning(f"Failed to parse content prefix: {e}")
            return None
        try:
            if marker == 0: # onchain metadata
                d = content.load_dict(key_length=256, value_deserializer=value_deserializer)
                # logger.info(f"Parsed onchain metadata: {d}")
                if not d:
                    logger.warning(f"Empty onchain metadata")
                    return None
                out = {}
                for hashed_key, key in KEYS:
                    if hashed_key in d:
                        out[key] = d[hashed_key]
                return out
            elif marker == 1: # offchain metadata
                uri = content.load_snake_string()
                return {KEY_URI: uri}
            else:
                logger.warning(f"Invalid marker: {marker}")
                return None
        except Exception as e:
            logger.warning(f"Failed to parse content: {e} {traceback.format_exc()}")
            return None
        return content
    
    def get_collection_emulator(self, db: DB, collection_address):
        if collection_address in self.collections_emulators:
            return self.collections_emulators[collection_address]
        res = db.get_latest_account_state(collection_address)
        if res:
            if res is None:
                logger.warning(f"No state for collection {collection_address}")
                return
            if res['data_boc'] is None:
                logger.warning(f"No data boc for collection {res}")
                return
            collection_emulator = self._prepare_emulator(res)
            self.collections_emulators[collection_address] = collection_emulator
            return collection_emulator
        return None
    
    def _do_parse(self, obj, db: DB, emulator: TvmEmulator):
        nft_address = Address(obj['account'])

        logger.info(f"Parsing NFT {nft_address}")
        try:
            init, index, collection_address, \
                owner_address, individual_content = self._execute_method(emulator, 'get_nft_data', [], db, obj)
        except Exception as e:
            if isinstance(e, EmulatorException) and e.result['vm_exit_code'] == 11:
                self.code_hash_blacklist.add(obj['code_hash'])
                logger.warning(f"Not an NFT: {e.result}, blacklisting code_hash")
                return
            raise e
        logger.info(f"Parsed NFT {nft_address}: {individual_content}")
        
        try:
            collection_address = collection_address.load_address()
        except Exception as e:
            logger.warning(f"Failed to load collection address: {e}")
            collection_address = None
        if owner_address is not None:
            try:
                owner_address = owner_address.load_address()
            except Exception as e:
                logger.warning(f"Failed to load owner address: {e}")
                return
        # Check that NFT address is not faked, i.e. collection returns the same address for its index
        if collection_address is not None:
            collection_emulator = self.get_collection_emulator(db, collection_address)
            if collection_emulator is None:
                logger.warning(f"No emulator for collection {collection_address}")
                return
            original_address, = self._execute_method(collection_emulator, 'get_nft_address_by_index', [index], db, obj)
            original_address = original_address.load_address()
            if original_address != nft_address:
                logger.warning(f"NFT address mismatch: {original_address} != {nft_address}")
                return
            if collection_address == TON_DNS:
                domain, = self._execute_method(emulator, 'get_domain', [], db, obj)
                content = {KEY_DOMAIN: domain.load_snake_string()}
            else:
                content, = self._execute_method(collection_emulator, 'get_nft_content', [index, individual_content], db, obj)
        else:
            content = individual_content

        if type(content) != dict:
            content = self.parse_metadata(content)
    
        logger.info(f"New NFT discovered: {nft_address}: {index} {collection_address} {owner_address} {obj['last_trans_lt']} {content}")
        db.insert_nft_item_v2(nft_address, index, collection_address, owner_address, obj['last_trans_lt'], obj['timestamp'], init != 0, content)
