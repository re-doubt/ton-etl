from typing import Dict, List, Set
from parsers.swaps.price_discovery import PriceDiscovery
from parsers.accounts.jetton_wallets_recover import JettonWalletsRecover
from parsers.accounts.nfts_recover import NFTsRecover
from parsers.message_contents.decode_comment import CommentsDecoder
from parsers.accounts.core_prices import CorePricesLSDstTON, CorePricesLSDtsTON, CorePricesStormTrade, CorePricesUSDT
from parsers.message.dedust_swap import DedustSwap
from parsers.message.stonfi_swap import StonfiSwap
from parsers.nft_transfer.nft_history import NftHistoryParser
from model.parser import Parser
from loguru import logger
import os

EMULATOR_PATH = os.environ.get("EMULATOR_LIBRARY")
MIN_SWAP_VOLUME_FOR_PRICE = int(os.environ.get("MIN_SWAP_VOLUME_FOR_PRICE", "1"))

_parsers = [
    DedustSwap(),
    NftHistoryParser(),
    StonfiSwap(),

    PriceDiscovery(MIN_SWAP_VOLUME_FOR_PRICE),

    CorePricesUSDT(),
    CorePricesLSDstTON(),
    CorePricesLSDtsTON(),
    # TON Vault
    CorePricesStormTrade(EMULATOR_PATH, Parser.uf2raw('EQDpJnZP89Jyxz3euDaXXFUhwCWtaOeRmiUJTi3jGYgF8fnj'),
                          Parser.uf2raw('EQCNY2AQ3ZDYwJAqx_nzl9i9Xhd_Ex7izKJM6JTxXRnO6n1F')),
    # NOT Vault
    CorePricesStormTrade(EMULATOR_PATH, Parser.uf2raw('EQAG8_BzwlWkmqb9zImr9RJjjgZZCLMOQXP9PR0B1PYHvfSS'),
                         Parser.uf2raw('EQAqtjTPy9vjuXUDaR4HgMPQfJBpIQorJLmRuk-ZQbRT-eiY')),
    # USDT Vault
    CorePricesStormTrade(EMULATOR_PATH, Parser.uf2raw('EQAz6ehNfL7_8NI7OVh1Qg46HsuC4kFpK-icfqK9J3Frd6CJ'),
                         Parser.uf2raw('EQCup4xxCulCcNwmOocM9HtDYPU8xe0449tQLp6a-5BLEegW')),

    NFTsRecover(EMULATOR_PATH),
    JettonWalletsRecover(EMULATOR_PATH),
    
    CommentsDecoder()
]

"""
dict of parsers, where key is the topic name
"""
def generate_parsers(names: Set)-> Dict[str, List[Parser]]: 
    out: Dict[str, List[Parser]] = {}

    for parser in _parsers:
        if names is not None:
            if type(parser).__name__ not in names:
                logger.info(f"Skipping parser {parser}, it is not in supported parsers list")
                continue
            else:
                logger.info(f"Adding parser {parser}: {type(parser).__name__}, {names}")
        for topic in parser.topics():
            if topic not in out:
                out[topic] = []
            out[topic].append(parser)
    return out
