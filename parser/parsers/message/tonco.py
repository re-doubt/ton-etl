from model.parser import Parser, TOPIC_MESSAGES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address
from model.dexswap import DEX_STON, DEX_STON_V2, DexSwapParsed
from parsers.message.swap_volume import estimate_volume

"""
TONCO CLMM DEX swap parsing based on https://docs.tonco.io/technical-reference/contracts/scenarios
The parser processes ROUTERV3_PAY_TO messages from the pool to the router. If the messages
processed successfully it means the swap was successful.
"""
ROUTER = Parser.uf2raw('EQC_-t0nCnOFMdp7E7qPxAOCbCWGFz-e3pwxb6tTvFmshjt5')

class TONCOSwap(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only internal messages sent by the router
        return obj.get("opcode", None) == Parser.opcode_signed(0xa1daa96d) and \
            obj.get("direction", None) == "in" and \
            obj.get("destination", None) == ROUTER
    

    def handle_internal(self, obj, db: DB):
        # raise
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0xa1daa96d
        query_id = cell.load_uint(64)
        owner0 = cell.load_address()
        owner1 = cell.load_address() # should be the same as owner0
        exit_code = cell.load_uint(32)
        seqno = cell.load_uint(64)
        coinsinfo_cell = cell.load_maybe_ref()
        logger.info(f"query_id: {query_id}, owner0: {owner0}, owner1: {owner1}, exit_code: {exit_code}, seqno: {seqno}")
        if coinsinfo_cell:
            coinsinfo_cell = coinsinfo_cell.begin_parse()
            amount0 = coinsinfo_cell.load_coins()
            jetton0_address = coinsinfo_cell.load_address()
            amount1 = coinsinfo_cell.load_coins()
            jetton1_address = coinsinfo_cell.load_address()
            logger.info(f"amount0: {amount0}, jetton0_address: {jetton0_address}, amount1: {amount1}, jetton1_address: {jetton1_address}")
        else:
            logger.info(f"No coinsinfo_cell for {obj.get('tx_hash')}")
            return
        
        # excesses_address = cell.load_address()
        # excesses_address_2 = cell.load_address()
        # exit_code = cell.load_uint(32)

        # if exit_code != 0xc64370e5: # swap_ok
        #     logger.debug(f"Message is not a payment to user, exit code {exit_code}")
        #     return

        # custom_payload = cell.load_maybe_ref()
    
        # additional_info = cell.load_ref().begin_parse()
        # fwd_ton_amount = additional_info.load_coins()
        # amount0_out = additional_info.load_coins()
        # token0_address = additional_info.load_address()
        # amount1_out = additional_info.load_coins()
        # token1_address = additional_info.load_address()
        # logger.info(f"{owner} {exit_code} {fwd_ton_amount} {amount0_out} {token0_address} {amount1_out} {token1_address}")


        # tx = Parser.require(db.is_tx_successful(Parser.require(obj.get('tx_hash', None))))
        # if not tx:
        #     logger.info(f"Skipping failed tx for {obj.get('tx_hash', None)}")
        #     return

        # parent_body = db.get_parent_message_body(obj.get('msg_hash'))
        # if not parent_body:
        #     logger.warning(f"Unable to find parent message for {obj.get('msg_hash')}")
        #     return
        # cell = Cell.one_from_boc(parent_body).begin_parse()
        
        # op_id = cell.load_uint(32) # 0x6664de2a
        # assert op_id == 0x6664de2a, f"Parent message for ston.fi swap is {op_id}"
        # parent_query_id = cell.load_uint(64)

        # from_user = cell.load_address()
        # left_amount = cell.load_coins()
        # right_amount = cell.load_coins()

        # dex_payload = cell.load_ref().begin_parse()
        # transferred_op = dex_payload.load_uint(32)
        # token_wallet1 = dex_payload.load_address()
        # swap_body = dex_payload.load_ref().begin_parse()
        # min_out = swap_body.load_coins()
        # receiver = swap_body.load_address()
        # fwd_gas = swap_body.load_coins()
        # custom_payload = swap_body.load_maybe_ref()
        # refund_fwd_gas = swap_body.load_coins()
        # refund_payload = swap_body.load_maybe_ref()
        # ref_fee = swap_body.load_uint(16)
        # ref_address = swap_body.load_address()

        # logger.info(f"token_wallet1: {token_wallet1}, left_amount: {left_amount}, right_amount: {right_amount}, ref_address: {ref_address}")
        
        # if token_wallet1 == token1_address:
        #     src_wallet_address = token0_address
        #     src_amount = left_amount - amount0_out
        #     dst_wallet_address = token1_address
        #     dst_amount = amount1_out
        # elif token_wallet1 == token0_address:
        #     src_wallet_address = token1_address
        #     src_amount = right_amount - amount1_out
        #     dst_wallet_address = token0_address
        #     dst_amount = amount0_out
        # else:
        #     logger.warning(f"Wallet addresses in swap message id={obj.get('msg_hash')} and payment message  don't match")
        
        # src_master = db.get_wallet_master(src_wallet_address)
        # dst_master = db.get_wallet_master(dst_wallet_address)
        # if not src_master:
        #     logger.warning(f"Wallet not found for {src_wallet_address}")
        #     return
        # if not dst_master:
        #     logger.warning(f"Wallet not found for {dst_wallet_address}")
        #     return

        # swap = DexSwapParsed(
        #     tx_hash=Parser.require(obj.get('tx_hash', None)),
        #     msg_hash=Parser.require(obj.get('msg_hash', None)),
        #     trace_id=Parser.require(obj.get('trace_id', None)),
        #     platform=DEX_STON_V2,
        #     swap_utime=Parser.require(obj.get('created_at', None)),
        #     swap_user=from_user,
        #     swap_pool=Parser.require(obj.get('source', None)),
        #     swap_src_token=src_master,
        #     swap_dst_token=dst_master,
        #     swap_src_amount=src_amount,
        #     swap_dst_amount=dst_amount,
        #     referral_address=ref_address,
        #     query_id=query_id,
        #     min_out=min_out,
        #     router=Parser.require(obj.get("destination", None))
        # )
        # estimate_volume(swap, db)
        # logger.info(swap)
        # db.serialize(swap)
        # db.discover_dex_pool(swap)
