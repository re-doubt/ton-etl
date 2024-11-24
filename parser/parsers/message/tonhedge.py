from model.parser import Parser, TOPIC_MESSAGES
from db import DB
from parsers.message.swap_volume import estimate_volume
from model.tonhedge import TonHedgeOptionPurchasedEvent

TON_HEDGE_POOL='0:57668d751f8c14ab76b3583a61a1486557bd746beeebbd4b2a65418b3fdb5471'
TON_HEDGE_USDT_WALLET='0:79dbd35ebe09cd2bcd561158fb6bc554a45892826b329c1c29160fde9ffa7c8f'

class TonHedgeOptionPurchased(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj) -> bool:
        # only external messages not blacklist
        return obj.get("opcode", None) == Parser.opcode_signed(0x0f8a7ea5) and \
            obj.get("direction", None) == "out" and \
            obj.get("destination", None) == TON_HEDGE_USDT_WALLET and \
            obj.get("source", None) == TON_HEDGE_POOL

    def handle_internal(self, obj, db: DB):
        cell=Parser.message_body(obj, db).begin_parse()
        cell.load_coins()
        destination=cell.load_address()
        cell.load_address()
        cell.load_maybe_ref()
        cell.load_coins()
        notification_body=cell if cell.load_uint(1) == 0 else cell.load_ref().begin_parse()

        if notification_body.remaining_bits() == 0:
            return

        response_op=notification_body.load_uint(32)

        if response_op != 0xad8e31ef:
            return

        notification_body.load_uint(64)
        exit_code=notification_body.load_uint(32)

        if exit_code != 0:
            return
        
        option_type='put' if notification_body.load_uint(8) == 0 else 'call'
        option_price=option_price
        opened_asset_price=notification_body.load_coins()
        strike_price=notification_body.load_coins()
        period=notification_body.load_uint(32)
        amount=notification_body.load_uint(32)
        purchased_at=notification_body.load_uint(64) * 1000
        id=notification_body.load_uint(64) if notification_body.remaining_bits() > 0 else Parser.require(obj.get("tx_lt"))
        initial_holder=notification_body.load_address() if notification_body.remaining_bits() > 0 else destination
        service_fee=notification_body.load_coins() if notification_body.remaining_bits() > 0 else 0
        
        # volumes
        premium=option_price - service_fee,
        notional_volume=amount * opened_asset_price
        volume=premium + notional_volume
        
        event = TonHedgeOptionPurchasedEvent(
            tx_hash=Parser.require(obj.get('tx_hash', None)),
            trace_id=Parser.require(obj.get('trace_id', None)),
            event_time=Parser.require(obj.get('created_at', None)),
            option_type=option_type,
            option_price=option_price,
            opened_asset_price=opened_asset_price,
            strike_price=strike_price,
            period=period,
            amount=amount,
            purchased_at=purchased_at,
            id=id,
            initial_holder=initial_holder,
            service_fee=service_fee,
            premium=premium,
            notional_volume=notional_volume,
            volume=volume,
        )

        db.serialize(event)
