from model.parser import Parser, TOPIC_MESSAGES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address
from model.dexswap import DexSwapParsed
from parsers.message.swap_volume import estimate_volume


# twin non-stable pools to avoid wrong prices estimation
# TODO - move to a special table?
BLACKLIST = set([
    Parser.uf2raw('EQA0a6c40n_Kejx_Wj0vowdeYCFYG9XnLdLMRHihXc27cng5'), 
    Parser.uf2raw('EQDpuDAY31FH2jM9PysFsmJ3aXMMReGYb_P65aDOXVYDcCJX')
])
class DedustSwap(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only external messages not blacklist
        return obj.get("opcode", None) == Parser.opcode_signed(0x9c610de3) and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", 'None') is None and \
            not obj.get("source", None) in BLACKLIST
    
    def _read_dedust_asset(self, cell):
        kind = cell.load_uint(4)
        if kind == 0:
            return Address("EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c")
        else:
            wc = cell.load_uint(8)
            account_id = cell.load_bytes(32) # 256 bits
            return Address((wc, account_id))

    def handle_internal(self, obj, db: DB):
        cell = Parser.message_body(obj, db).begin_parse()
        op_id = cell.load_uint(32) # swap#9c610de3
        asset_in = self._read_dedust_asset(cell)
        asset_out = self._read_dedust_asset(cell)
        amount_in = cell.load_coins()
        amount_out = cell.load_coins()
        if amount_in == 0 or amount_out == 0:
            logger.info(f"Skipping zero amount swap for {obj}")
            return
        payload = cell.load_ref().begin_parse()
        sender_addr = payload.load_address()
        referral_addr = payload.load_address()
        reserve0 = payload.load_coins()
        reserve1 = payload.load_coins()

        swap = DexSwapParsed(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            msg_hash=Parser.require(obj.get('msg_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            platform="dedust",
            swap_utime=Parser.require(obj.get('created_at', None)),
            swap_user=sender_addr,
            swap_pool=Parser.require(obj.get('source', None)),
            swap_src_token=asset_in,
            swap_dst_token=asset_out,
            swap_src_amount=amount_in,
            swap_dst_amount=amount_out,
            referral_address=referral_addr,
            reserve0=reserve0,
            reserve1=reserve1
        )
        estimate_volume(swap, db)
        db.serialize(swap)
        db.discover_dex_pool(swap)
