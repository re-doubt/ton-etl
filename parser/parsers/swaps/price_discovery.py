from model.parser import Parser, TOPIC_DEX_SWAPS
from loguru import logger
from db import DB
import base64
from pytoniq_core import Cell, Address
from model.dextrade import DexTrade
from parsers.utils import decode_decimal
from parsers.message.swap_volume import QUOTE_ASSET_TYPE_LSD, QUOTE_ASSET_TYPE_OTHER, QUOTE_ASSET_TYPE_STABLE, QUOTE_ASSET_TYPE_TON, USDT, base_quote, estimate_volume


"""
The parser uses parsed DEX swap events to estimate price. Price estimation is following:
* if volume_usd is null or below min_volume param the event is skipped (to avoid low volume swaps)
* detect quote asset (according to the rules below):
  - TON (or wrapped TON) is always a quote
  - if the pool has stablecoin it is a quote asset
  - if the pool has LSD it is a quote asset
  - otherwise skip this pool
* save price for this pool
*  calculate weighted average price for the base asset using latest prices for all pools and
based on the trading volume for the last 1h


CREATE TABLE prices.agg_prices (
    id serial primary key,
	base varchar NULL,
	price_time int8 NULL,
	price_ton numeric NULL,
    price_usd numeric NULL,
    created timestamp NULL,
	updated timestamp null,
	unique (base, price_time)
);
"""
class PriceDiscovery(Parser):

    def __init__(self, min_volume, average_window=1800) -> None:
        super().__init__()
        self.min_volume = min_volume
        self.average_window = average_window
    
    def topics(self):
        return [TOPIC_DEX_SWAPS]

    def predicate(self, obj) -> bool:
        return obj.get('volume_usd', None) is not None


    def handle_internal(self, obj, db: DB):
        swap_utime = obj['swap_utime']
        volume_usd = decode_decimal(obj['volume_usd'])
        if volume_usd < self.min_volume:
            return
        
        # determine base and quote assets
        base, quote, quote_asset_type = base_quote(obj['swap_src_token'], obj['swap_dst_token'])
        # ignore token/token swaps to avoid price manipulation
        if quote_asset_type == QUOTE_ASSET_TYPE_OTHER:
            return
        # determine base and quote amounts
        base_amount = decode_decimal(obj['swap_src_amount'])
        quote_amount = decode_decimal(obj['swap_dst_amount'])
        if quote == obj['swap_src_token']:
            base_amount, quote_amount = quote_amount, base_amount

        price = quote_amount / base_amount
        if quote_asset_type == QUOTE_ASSET_TYPE_TON:
            price_ton = price
            ton_price = db.get_core_price(USDT, swap_utime)
            price_usd = price_ton * ton_price
        if quote_asset_type == QUOTE_ASSET_TYPE_STABLE:
            price_usd = price
            ton_price = db.get_core_price(USDT, swap_utime)
            price_ton = price_usd / ton_price
        if quote_asset_type == QUOTE_ASSET_TYPE_LSD:
            lsd_price = db.get_core_price(quote, swap_utime)
            if lsd_price is None:
                logger.warning("Price is empty for {} at {}", quote, swap_utime)
                return
            price_ton = price * lsd_price
            ton_price = db.get_core_price(USDT, swap_utime)
            price_ton = price_ton * ton_price

        trade = DexTrade(
            tx_hash=obj['tx_hash'],
            platform=obj['platform'],
            swap_utime=swap_utime,
            swap_pool=obj['swap_pool'],
            base=base,
            quote=quote,
            base_amount=base_amount,
            quote_amount=quote_amount,
            price=price,
            price_ton=price_ton,
            price_usd=price_usd,
            volume_ton=volume_usd,
            volume_usd=volume_usd
        )
        db.serialize(trade)
        db.update_agg_prices(base, swap_utime, self.average_window)
