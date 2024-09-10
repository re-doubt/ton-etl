from dataclasses import dataclass


@dataclass
class SaleContract:
    name: str
    signature: list
    marketplace_pos: int
    nft_pos: int
    price_pos: int
    owner_pos: int
    is_auction: bool


SALE_CONTRACTS = {
    'gnj0xSM95vvtyWmvUZNEp6m//FRIVtuphqlcC8+Fcck=': SaleContract(
        name='nft-fixprice-sale-v2',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        # 0x46495850, is_complete, created_at,  marketplace, nft, nft_owner, full_price, fee_address, fee, royalty_address, royalty_amount
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
    ),
    'MgUN+sRPZIZrzIbyzZ4TBf6dyts5WcACI3z7CQLUQyM=': SaleContract(
        name='nft-fixprice-sale-v3',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
        # the same as v2
    ),
    'R2O/IVsms3ndyBpJSxZu683RIqAhUXAiVt1rKJuCVG4=': SaleContract(
        name='disintar1',
        signature=['address', 'address', 'address', 'int', 'int', 'address', 'int', 'int', 'address', 'address', 'int', 'address'],
        # marketplace, nft, deployer, price, fee, royalty_destination, royalty_fee, is_ton, jetton_addr, limited, end_at, master
        marketplace_pos=0,
        nft_pos=1,
        price_pos=3,
        owner_pos=2,
        is_auction=False
    ),
    'hzmoLuczOVjvz3f3jGJOohQP7oBBW7GYfWocmUTZKZc=': SaleContract(
        name='disintar2',
        signature=['address', 'address', 'address', 'int', 'int', 'address', 'int'],
        # marketplace, nft, deployer, price, fee, royalty_destination, royalty_fee
        marketplace_pos=0,
        nft_pos=1,
        price_pos=3,
        owner_pos=2,
        is_auction=False
    ),
    'ZmiHL6eXBUQ//UdSPo6eqfdquZ+aC1nSfej4GhwnudQ=': SaleContract(
        name='gg_auction1',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int', 'int', 'address', 'int', 'int', 'int', 'int', 'int', 'int', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=True
    ),
    '/ACindAgW83MDT/7nKOMw8jBWexg2KpUMkCpLxBZLUA=': SaleContract(
        name='gg_auction2',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int', 'int', 'address', 'int', 'int', 'int', 'int', 'int', 'int', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=True
    ),
    'XeQ8nKCKDX5eIbmYUIFQqAYt/Gsh4Q7+jraIOO6er2g=': SaleContract(
        name='disintar3',
        signature=['address', 'address', 'address', 'int', 'int', 'address', 'int'],
        # marketplace, nft, deployer, price, fee, royalty_destination, royalty_fee
        marketplace_pos=0,
        nft_pos=1,
        price_pos=3,
        owner_pos=2,
        is_auction=False
    ),
    '3STlTKqhorjnBRT8Ob/Ey8SxVDynTSzG/A6zVCnhudU=': SaleContract(
        name='unknown',
        signature=['address', 'address', 'address', 'int', 'int', 'address', 'int'],
        # marketplace, nft, owner, full_price, market_fee, royalty_address, royalty_amount
        marketplace_pos=0,
        nft_pos=1,
        price_pos=3,
        owner_pos=2,
        is_auction=False
    ),
    '3rU7bFdlwebNI4v0e8XoO6WWvcwEsLhM1Qqx5HSgjzE=': SaleContract(
        name='nft-fixprice-sale-v3r2',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        # magic, is_complete, created_at, marketplace, nft, owner, full_price, market_fee_address, market_fee, royalty_address, royalty_amount
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
    ),
    'G9nFo5v/t6DzQViLXdkrgTqEK/Ze8UEJOCIAzq+Pct8=': SaleContract(
        name='gg_auction3',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int', 'int', 'address', 'int', 'int', 'int', 'int', 'int', 'int', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=True
    ),
    'y3U6q5fvuBNcDSktQCumPa+K0vw8/PEzSnqjCCMMf1c=': SaleContract(
        name='raffles',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
    ),
    'JCIfpXHlQuBVx3vt/b9SfHr0YM/cfzRMRQeHtM+h600=': SaleContract(
        name='gg_nft_sale_v2',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
    ),
    'u29ireD+stefqzuK6/CTCvmFU99gCTsgJ/Covxab/Ow=': SaleContract(
        name='gg_auction_v3r3',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int', 'int', 'address', 'int', 'int', 'int', 'int', 'int', 'int', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=True
    ),
    'tjbeUWfIsnNE4pIb/8nKCzQFIhoxbzdM6EbvB5nSD1E=': SaleContract(
        name='nft_sale_v2',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
    ),
    'Serdan6AL8XjmjtQ484xqrfwKrJNduG8tfxjEUAF0SY=': SaleContract(
        name='nft_sale_v2',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=False
    ),
    'jscuKzKOK5hY93Fy2Qpo4ZSuaVzgXbrL6S412r6XV2E=': SaleContract(
        name='auction',
        signature=['int', 'int', 'int', 'address', 'address', 'address', 'int', 'address', 'int', 'address', 'int', 'int', 'address', 'int', 'int', 'int', 'int', 'int', 'int', 'int'],
        marketplace_pos=3,
        nft_pos=4,
        price_pos=6,
        owner_pos=5,
        is_auction=True
    ),

    # TODO support more sales contract
}
