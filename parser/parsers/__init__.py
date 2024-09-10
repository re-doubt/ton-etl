from typing import Dict, List, Set
from parsers.message.dedust_swap import DedustSwap
from parsers.nft_transfer.nft_history import NftHistoryParser
from model.parser import Parser

_parsers = [
    DedustSwap(),
    NftHistoryParser(),
]

"""
dict of parsers, where key is the topic name
"""
def generate_parsers(names: Set)-> Dict[str, List[Parser]]: 

    # TODO add suppoer for filtering by names
    out: Dict[str, List[Parser]] = {}

    for parser in _parsers:
        for topic in parser.topics():
            if topic not in out:
                out[topic] = []
            out[topic].append(parser)
    return out
