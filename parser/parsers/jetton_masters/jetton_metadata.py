import time
from loguru import logger

from db import DB
from model.parser import TOPIC_JETTON_MASTERS, Parser, TOPIC_JETTON_WALLETS
from model.jetton_metadata import JettonMetadata

OFFCHAIN_UPDATE_TIME_INTERVAL = 86400
OFFCHAIN_UPDATE_STATUS_ERROR = -1
OFFCHAIN_UPDATE_STATUS_OK = 1
OFFCHAIN_UPDATE_STATUS_NO = 0

"""
The parser extracts on-chain and off-chainmetadata from jetton masters and stores it in the database.
"""
class JettonMastersMetadataParser(Parser):

    def topics(self):
        return [TOPIC_JETTON_MASTERS]

    def predicate(self, obj) -> bool:
        return True

    def handle_internal(self, obj: dict, db: DB):
        address = Parser.require(obj.get("address", None))
        metadata = db.get_jetton_metadata(address)
        prev_ts_onchain = metadata.update_time_onchain if metadata else 0
        prev_ts_offchain = metadata.update_time_offchain if metadata else 0
        updated = False
        if metadata:
            logger.info(f"Jetton metadata for {address} already exists")
            if metadata.mintable != obj.get("mintable", None):
                updated = True
                logger.info(f"Mintable flag has been changed for {address}: {metadata.mintable} -> {obj.get('mintable', None)}")
                metadata.mintable = obj.get("mintable", None)
            if metadata.admin_address != obj.get("admin_address", None):
                updated = True
                logger.info(f"Admin address has been changed for {address}: {metadata.admin_address} -> {obj.get('admin_address', None)}")
                metadata.admin_address = obj.get("admin_address", None)
            if metadata.jetton_content_onchain != obj.get("jetton_content", None):
                updated = True
                logger.info(f"Jetton content has been changed for {address}: {metadata.jetton_content_onchain} -> {obj.get('jetton_content', None)}")
                metadata.jetton_content_onchain = obj.get("jetton_content", None)
            if metadata.jetton_wallet_code_hash != obj.get("jetton_wallet_code_hash", None):
                updated = True
                logger.info(f"Jetton wallet code hash has been changed for {address}: {metadata.jetton_wallet_code_hash} -> {obj.get('jetton_wallet_code_hash', None)}")
                metadata.jetton_wallet_code_hash = obj.get("jetton_wallet_code_hash", None)
            if metadata.code_hash != obj.get("code_hash", None):
                updated = True
                logger.info(f"Code hash has been changed for {address}: {metadata.code_hash} -> {obj.get('code_hash', None)}")
                metadata.code_hash = obj.get("code_hash", None)
        else:
            logger.info(f"Jetton metadata for {address} does not exist, creating")
            metadata = JettonMetadata(
                address=address,
                update_time_onchain=obj.get("last_tx_now", None),
                mintable=obj.get("mintable", None),
                admin_address=obj.get("admin_address", None),
                jetton_content_onchain=obj.get("jetton_content", None),
                jetton_wallet_code_hash=obj.get("jetton_wallet_code_hash", None),
                code_hash=obj.get("code_hash", None)
            )
            updated = True
        if updated and (not metadata.update_time_offchain or metadata.update_time_offchain < time.time() - OFFCHAIN_UPDATE_TIME_INTERVAL):
            logger.info(f"Updating offchain metadata for {address}: {obj.get('jetton_content', None)}")
            raise
            try:
                pass
            except Exception as e:
                logger.error(f"Error updating offchain metadata for {address}: {e}")
                metadata.metadata_status = OFFCHAIN_UPDATE_STATUS_ERROR
                metadata.update_time_offchain = time.time()
        if updated:
            logger.info(f"Upserting jetton metadata for {address}")
            db.upsert_jetton_metadata(metadata, prev_ts_onchain, prev_ts_offchain)
