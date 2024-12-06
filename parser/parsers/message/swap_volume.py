"""
Utility method to estimate swap volume in TON and USDT
"""
from model.dexswap import DexSwapParsed
from db import DB
from loguru import logger
from model.parser import Parser
from pytoniq_core import Address

from model.dexpool import DexPool

USDT = Parser.uf2raw('EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs')
jUSDT = Parser.uf2raw('EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA')
jUSDC = Parser.uf2raw('EQB-MPwrd1G6WKNkLz_VnV6WqBDd142KMQv-g1O-8QUA3728')
pTON = Parser.uf2raw('EQCM3B12QK1e4yZSf8GtBRT0aLMNyEsBc_DhVfRRtOEffLez') # ston.fi v1
pTONv2 = Parser.uf2raw('EQBnGWMCf3-FZZq1W4IWcWiGAc3PHuZ0_H-7sad2oY00o83S') # ston.fi v2
WTON_Megaton = Parser.uf2raw('EQCajaUU1XXSAjTD-xOV7pE49fGtg4q8kF3ELCOJtGvQFQ2C')
WTON_Stonfi = Parser.uf2raw('EQDQoc5M3Bh8eWFephi9bClhevelbZZvWhkqdo80XuY_0qXv') # deprecated
wTTon_TONCO = Parser.uf2raw('EQCUnExmdgwAKADi-j2KPKThyQqTc7U650cgM0g78UzZXn9J')
TON = Parser.uf2raw('EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c')
stTON = Parser.uf2raw('EQDNhy-nxYFgUqzfUzImBEP67JqsyMIcyk2S5_RwNNEYku0k')
tsTON = Parser.uf2raw('EQC98_qAmNEptUtPc7W6xdHh_ZHrBUFpw5Ft_IzNU20QAJav')
oUSDT = Parser.uf2raw('EQC_1YoM8RBixN95lz7odcF3Vrkc_N8Ne7gQi7Abtlet_Efi')
oUSDC = Parser.uf2raw('EQC61IQRl0_la95t27xhIpjxZt32vl1QQVF2UgTNuvD18W-4')

STABLES = [USDT, jUSDT, jUSDC]
TONS = [pTON, TON, pTONv2, WTON_Megaton, WTON_Stonfi, wTTon_TONCO]
LSDS = [stTON, tsTON]
ORBIT_STABLES = [oUSDT, oUSDC]
STABLES_INCLUDING_ORBIT = STABLES + ORBIT_STABLES
# Orbit bridge was hacked on 2024-01-01 (see https://blockworks.co/news/80-million-lost-orbit-bridge)
# that resulted in de-peg of oUSDT and oUSDC so we will not consider them as stablecoins after the hack date
ORBIT_HACK_TIMESTAMP = 1703980800

QUOTE_ASSET_TYPE_TON = "TON"
QUOTE_ASSET_TYPE_STABLE = "STABLE"
QUOTE_ASSET_TYPE_LSD = "LSD"
QUOTE_ASSET_TYPE_OTHER = "OTHER"

"""
Deterministically returns base and quote tokens and quote asset type
"""
def base_quote(left: str, right: str) -> (str, str, str):
    if left in STABLES_INCLUDING_ORBIT and right in STABLES_INCLUDING_ORBIT:
        return (min(left, right), max(left, right), QUOTE_ASSET_TYPE_STABLE)
    if left in STABLES_INCLUDING_ORBIT:
        return (right, left, QUOTE_ASSET_TYPE_STABLE)
    if right in STABLES_INCLUDING_ORBIT:
        return (left, right, QUOTE_ASSET_TYPE_STABLE)
    if left in TONS and right in TONS: # meaningless..
        return (min(left, right), min(left, right), QUOTE_ASSET_TYPE_TON)
    if left in TONS:
        return (right, left, QUOTE_ASSET_TYPE_TON)
    if right in TONS:
        return (left, right, QUOTE_ASSET_TYPE_TON)
    if left in LSDS:
        return (right, left, QUOTE_ASSET_TYPE_LSD)
    if right in LSDS:
        return (left, right, QUOTE_ASSET_TYPE_LSD)
    return (min(left, right), max(left, right), QUOTE_ASSET_TYPE_OTHER)

"""
Estimates swap volume using current core prices
Updates swap inplace
"""
def estimate_volume(swap: DexSwapParsed, db: DB):
    volume_usd, volume_ton = None, None
    ton_price = db.get_core_price(USDT, swap.swap_utime)
    if ton_price is None:
        logger.warning(f"No TON price found for {swap.swap_utime}")
        return
    ton_price = ton_price * 1e3 # normalize on decimals difference
    def normalize_addr(a):
        if type(a) == Address:
            return a.to_str(is_user_friendly=False).upper()
        else:
            return a
    swap_src_token = normalize_addr(swap.swap_src_token)
    swap_dst_token = normalize_addr(swap.swap_dst_token)
    if swap_src_token in STABLES or (swap_src_token in ORBIT_STABLES and swap.swap_utime < ORBIT_HACK_TIMESTAMP):
        volume_usd = swap.swap_src_amount / 1e6
        volume_ton = volume_usd / ton_price
    elif swap_dst_token in STABLES or (swap_dst_token in ORBIT_STABLES and swap.swap_utime < ORBIT_HACK_TIMESTAMP):
        volume_usd = swap.swap_dst_amount / 1e6
        volume_ton = volume_usd / ton_price

    elif swap_src_token in TONS:
        volume_ton = swap.swap_src_amount / 1e9
        volume_usd = volume_ton * ton_price
    elif swap_dst_token in TONS:
        volume_ton = swap.swap_dst_amount / 1e9
        volume_usd = volume_ton * ton_price

    elif swap_src_token in LSDS:
        lsd_price = db.get_core_price(swap_src_token, swap.swap_utime)
        if not lsd_price:
            logger.warning(f"No price for {swap_src_token} for {swap.swap_utime}")
            return
        volume_ton = swap.swap_src_amount / 1e9 * lsd_price
        volume_usd = volume_ton * ton_price
    elif swap_dst_token in LSDS:
        lsd_price = db.get_core_price(swap_dst_token, swap.swap_utime)
        if not lsd_price:
            logger.warning(f"No price for {swap_dst_token} for {swap.swap_utime}")
            return
        volume_ton = swap.swap_dst_amount / 1e9 * lsd_price
        volume_usd = volume_ton * ton_price

    # TODO add support for other combinations
    
    if volume_usd is not None:
        swap.volume_usd = volume_usd
        swap.volume_ton = volume_ton
    

"""
Estimates pool TVL using current core prices
Updates swap pool inplace
"""
def estimate_tvl(pool: DexPool, db: DB):
    tvl_usd, tvl_ton = None, None
    ton_price = db.get_core_price(USDT, pool.last_updated)
    if ton_price is None:
        logger.warning(f"No TON price found for {pool.last_updated}")
        return
    ton_price = ton_price * 1e3 # normalize on decimals difference
    def normalize_addr(a):
        if type(a) == Address:
            return a.to_str(is_user_friendly=False).upper()
        else:
            return a
    jetton_left = normalize_addr(pool.jetton_left)
    jetton_right = normalize_addr(pool.jetton_right)
    if jetton_left in STABLES or (jetton_left in ORBIT_STABLES and pool.last_updated < ORBIT_HACK_TIMESTAMP):
        tvl_usd = pool.reserves_left / 1e6 * 2
        tvl_ton = tvl_usd / ton_price
    elif jetton_right in STABLES or (jetton_right in ORBIT_STABLES and pool.last_updated < ORBIT_HACK_TIMESTAMP):
        tvl_usd = pool.reserves_right / 1e6 * 2
        tvl_ton = tvl_usd / ton_price

    elif jetton_left in TONS:
        tvl_ton = pool.reserves_left / 1e9 * 2
        tvl_usd = tvl_ton * ton_price
    elif jetton_right in TONS:
        tvl_ton = pool.reserves_right / 1e9 * 2
        tvl_usd = tvl_ton * ton_price

    elif jetton_left in LSDS:
        lsd_price = db.get_core_price(jetton_left, pool.last_updated)
        if not lsd_price:
            logger.warning(f"No price for {jetton_left} for {pool.last_updated}")
            return
        tvl_ton = pool.reserves_left / 1e9 * lsd_price * 2
        tvl_usd = tvl_ton * ton_price
    elif jetton_right in LSDS:
        lsd_price = db.get_core_price(jetton_right, pool.last_updated)
        if not lsd_price:
            logger.warning(f"No price for {jetton_right} for {pool.last_updated}")
            return
        tvl_ton = pool.reserves_right / 1e9 * lsd_price * 2
        tvl_usd = tvl_ton * ton_price
    else:
        left_price = db.get_agg_price(jetton_left, pool.last_updated)
        right_price = db.get_agg_price(jetton_right, pool.last_updated)
        if not left_price :
            logger.warning(f"No price for {jetton_left} for {pool.last_updated}")
            return
        if not right_price :
            logger.warning(f"No price for {right_price} for {pool.last_updated}")
            return
        tvl_ton = (pool.reserves_left * left_price + pool.reserves_right * right_price) / 1e9
        tvl_usd = tvl_ton * ton_price
        pool.is_liquid = False
    
    if tvl_ton is not None:
        pool.tvl_ton = tvl_ton
        pool.tvl_usd = tvl_usd
