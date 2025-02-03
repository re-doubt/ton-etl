import importlib
import pytest
from unittest.mock import Mock
from pytoniq_core import Address

from parser.parsers.message.swap_volume import estimate_tvl
from parser.model.dexpool import DexPool


TON = Address("EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c")
USDT = Address("EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs")
oUSDT = Address("EQC_1YoM8RBixN95lz7odcF3Vrkc_N8Ne7gQi7Abtlet_Efi")
tsTON = Address("EQC98_qAmNEptUtPc7W6xdHh_ZHrBUFpw5Ft_IzNU20QAJav")
NOT = Address("EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT")
STORM = Address("EQBsosmcZrD6FHijA7qWGLw5wo_aH8UN435hi935jJ_STORM")


@pytest.mark.parametrize(
    "jetton_left, jetton_right, reserves_left, reserves_right, last_updated, "
    "usdt_core_price, tston_core_price, not_agg_price, storm_agg_price, non_liquid_pools_tvl, "
    "res_tvl_usd, res_tvl_ton, res_is_liquid",
    [
        # TONS-STABLES pool, usual case
        (TON, USDT, 2e15, 1e13, 1738000000, 0.005, 1.05, 0.001, 0.005, "0", 2e7, 4e6, True),
        # TONS-STABLES pool, tokens are mirrored
        (USDT, TON, 1e13, 2e15, 1738000000, 0.005, 1.05, 0.001, 0.005, "0", 2e7, 4e6, True),
        # TONS-STABLES pool, no TON price found
        (TON, USDT, 2e15, 1e13, 1738000000, None, 1.05, 0.001, 0.005, "0", None, None, True),
        # TONS-STABLES pool, TON price = 0
        (TON, USDT, 2e15, 1e13, 1738000000, 0, 1.05, 0.001, 0.005, "0", None, None, True),
        # TONS-STABLES pool, usual case, NON_LIQUID_POOLS_TVL is set to '1'
        (TON, USDT, 2e15, 1e13, 1738000000, 0.005, 1.05, 0.001, 0.005, "1", 2e7, 4e6, True),
        # TONS-ORBIT_STABLES pool, time after ORBIT_HACK_TIMESTAMP
        (TON, oUSDT, 2e13, 1e11, 1738000000, 0.005, 1.05, 0.001, 0.005, "0", None, None, True),
        # TONS-ORBIT_STABLES pool, time befor ORBIT_HACK_TIMESTAMP
        (TON, oUSDT, 2e13, 1e11, 1703900000, 0.005, 1.05, 0.001, 0.005, "0", 2e5, 4e4, True),
        # LSDS-STABLES pool, usual case
        (tsTON, USDT, 2e15, 1e13, 1738000000, 0.005, 1.05, 0.001, 0.005, "0", 2.05e7, 4.1e6, True),
        # LSDS-STABLES pool, no price for LSD
        (tsTON, USDT, 2e15, 1e13, 1738000000, 0.005, None, 0.001, 0.005, "0", None, None, True),
        # TONS-JETTONS pool, usual case
        (TON, NOT, 1e12, 1e15, 1738000000, 0.005, 1.05, 0.001, 0.005, "0", 1e4, 2e3, True),
        # TONS-JETTONS pool, no price for jetton
        (TON, NOT, 1e12, 1e15, 1738000000, 0.005, 1.05, None, 0.005, "0", None, None, True),
        # TONS-JETTONS pool, usual case, NON_LIQUID_POOLS_TVL is set to '1'
        (TON, NOT, 1e12, 1e15, 1738000000, 0.005, 1.05, 0.001, 0.005, "1", 1e4, 2e3, True),
        # JETTONS-JETTONS pool, usual case, NON_LIQUID_POOLS_TVL is set to '0'
        (NOT, STORM, 5e15, 1e15, 1738000000, 0.005, 1.05, 0.001, 0.005, "0", None, None, False),
        # JETTONS-JETTONS pool, usual case, NON_LIQUID_POOLS_TVL is set to '1'
        (NOT, STORM, 5e15, 1e15, 1738000000, 0.005, 1.05, 0.001, 0.005, "1", 5e4, 1e4, False),
        # JETTONS-JETTONS pool, no price for jetton, NON_LIQUID_POOLS_TVL is set to '1'
        (NOT, STORM, 5e15, 1e15, 1738000000, 0.005, 1.05, 0.001, None, "1", None, None, False),
        # JETTONS-JETTONS pool, no price for both jettons, NON_LIQUID_POOLS_TVL is set to '1'
        (NOT, STORM, 5e15, 1e15, 1738000000, 0.005, 1.05, None, None, "1", None, None, False),
    ],
)
def test_estimate_tvl(
    monkeypatch,
    jetton_left,
    jetton_right,
    reserves_left,
    reserves_right,
    last_updated,
    usdt_core_price,
    tston_core_price,
    not_agg_price,
    storm_agg_price,
    non_liquid_pools_tvl,
    res_tvl_usd,
    res_tvl_ton,
    res_is_liquid,
):
    monkeypatch.setenv("NON_LIQUID_POOLS_TVL", non_liquid_pools_tvl)
    import parser.parsers.message.swap_volume

    importlib.reload(parser.parsers.message.swap_volume)

    core_price_mapping = {
        (USDT.to_str(False).upper(), last_updated): usdt_core_price,
        (tsTON.to_str(False).upper(), last_updated): tston_core_price,
    }
    agg_price_mapping = {
        (NOT.to_str(False).upper(), last_updated): not_agg_price,
        (STORM.to_str(False).upper(), last_updated): storm_agg_price,
    }
    db = Mock()
    db.get_core_price.side_effect = lambda jetton, last_updated: core_price_mapping.get((jetton, last_updated), None)
    db.get_agg_price.side_effect = lambda jetton, last_updated: agg_price_mapping.get((jetton, last_updated), None)

    pool = DexPool(
        pool="some_pool_address",
        platform="some_platform",
        jetton_left=jetton_left,
        jetton_right=jetton_right,
        reserves_left=reserves_left,
        reserves_right=reserves_right,
        last_updated=last_updated,
        tvl_usd=None,
        tvl_ton=None,
        is_liquid=True,
    )

    estimate_tvl(pool, db)

    assert pool.tvl_usd == res_tvl_usd
    assert pool.tvl_ton == res_tvl_ton
    assert pool.is_liquid == res_is_liquid
