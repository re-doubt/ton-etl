from model.parser import Parser, TOPIC_ACCOUNT_STATES
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address
from model.dexswap import DexSwapParsed

"""
Discovers prices for the core assets, i.e.:
* TON itself, based on TON/USDT pool reserves
* stTON and tsTON
"""
class CorePrices(Parser):
    """
    account - address to look updates for
    asset - item for core prices table
    """
    def __init__(self, account, asset, update_interval=60):
        self.account = account
        self.asset = asset
        self.latest_update = None
        self.latest_price = None
        self.update_interval = update_interval
    
    def topics(self):
        return [TOPIC_ACCOUNT_STATES]

    def predicate(self, obj) -> bool:
        return obj.get("account", None) == self.account
    
    """
    Handle price updates and store in the DB
    """
    def update_price(self, price, obj, db: DB):
        timestamp = obj.get('timestamp')
        if self.latest_update is not None:
            if timestamp < self.latest_update + self.update_interval:
                logger.debug(f"Price timestamp for {self.asset} is before latest update + update interval, skipping")
                return

            if price == self.latest_price:
                logger.info(f"Price for asset {self.asset} is the same: {price}")
                return

        self.latest_update = timestamp
        self.latest_price = price
        db.insert_core_price(self.asset, price, obj)
    

class CorePricesUSDT(CorePrices):
    def __init__(self, update_interval=60):
        super().__init__(account=Parser.uf2raw('EQD8TJ8xEWB1SpnRE4d89YO3jl0W0EiBnNS4IBaHaUmdfizE'), 
                         asset=Parser.uf2raw('EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs'), 
                         update_interval=update_interval)

    def handle_internal(self, obj, db: DB):
        cell = Cell.one_from_boc(Parser.require(obj.get('data_boc'))).begin_parse()

        cell = cell.load_ref().begin_parse()
        cell.load_coins() # proto fee
        cell.load_coins() # proto fee
        cell.load_address() # proto fee address
        reserve0 = cell.load_coins()
        reserve1 = cell.load_coins()
        
        logger.info(f"TON/USDT pool: {reserve0}, {reserve1}")
        self.update_price(1.0 * reserve0 / reserve1, obj, db)

# TODO stTON and tsTON prices

