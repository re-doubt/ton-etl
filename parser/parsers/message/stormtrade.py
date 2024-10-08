from loguru import logger

from db import DB
from model.parser import Parser, TOPIC_MESSAGES
from model.stormtrade import StormExecuteOrder, StormCompleteOrder, StormUpdatePosition, StormTradeNotification


class StormExecuteOrderParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj: dict) -> bool:
        return obj.get("opcode") == Parser.opcode_signed(0xde1ddbcc) and obj.get("direction") == "in"

    def handle_internal(self, obj: dict, db: DB):
        logger.info(f"Parsing storm execute_order message {Parser.require(obj.get('msg_hash'))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0xde1ddbcc

        direction = cell.load_uint(1)
        order_index = cell.load_uint(3)
        trader_addr = cell.load_address()
        prev_addr = cell.load_address()
        ref_addr = cell.load_address()
        executor_index = cell.load_uint(32)

        order = cell.load_ref().begin_parse()
        position = cell.load_ref().begin_parse()
        oracle_payload = cell.load_ref().begin_parse().load_ref().begin_parse()

        order_type = order.load_uint(4)

        if order_type in (0, 1):
            """
            stop_loss_order$0000 / take_profit_order$0001 
            expiration:uint32 direction:Direction 
            amount:Coins triger_price:Coins = SLTPOrder
            """
            expiration = order.load_uint(32)
            direction_order = order.load_uint(1)
            amount = order.load_coins()
            triger_price = order.load_coins()
            leverage, limit_price, stop_price, stop_triger_price, take_triger_price = None, None, None, None, None

        elif order_type in (2, 3):
            """
            stop_limit_order$0010 / market_order$0011 
            expiration:uint32 direction:Direction
            amount:Coins leverage:uint64
            limit_price:Coins stop_price:Coins
            stop_triger_price:Coins take_triger_price:Coins = LimitMarketOrder
            """
            expiration = order.load_uint(32)
            direction_order = order.load_uint(1)
            amount = order.load_coins()
            leverage = order.load_uint(64)
            limit_price = order.load_coins()
            stop_price = order.load_coins()
            stop_triger_price = order.load_coins()
            take_triger_price = order.load_coins()
            triger_price = None

        else:
            raise Exception(f"Order_type {order_type} is not supported")

        """
        position#_ size:int128 direction:Direction 
        margin:Coins open_notional:Coins 
        last_updated_cumulative_premium:int64
        fee:uint32 discount:uint32 rebate:uint32 
        last_updated_timestamp:uint32 = PositionData
        """
        position_size = position.load_int(128)
        direction_position = position.load_uint(1)
        margin = position.load_coins()
        open_notional = position.load_coins()
        last_updated_cumulative_premium = position.load_int(64)
        fee = position.load_uint(32)
        discount = position.load_uint(32)
        rebate = position.load_uint(32)
        last_updated_timestamp = position.load_uint(32)

        """
        price_data#_ price:Coins spread:Coins timestamp:uint32 asset_id:uint16 = OraclePriceData
        """
        oracle_price = oracle_payload.load_coins()
        spread = oracle_payload.load_coins()
        oracle_timestamp = oracle_payload.load_uint(32)
        asset_id = oracle_payload.load_uint(16)

        execute_order = StormExecuteOrder(
            tx_hash=Parser.require(obj.get("tx_hash")),
            msg_hash=Parser.require(obj.get("msg_hash")),
            trace_id=Parser.require(obj.get("trace_id")),
            utime=Parser.require(obj.get("created_at")),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash")))),
            direction=direction,
            order_index=order_index,
            trader_addr=trader_addr,
            prev_addr=prev_addr,
            ref_addr=ref_addr,
            executor_index=executor_index,
            order_type=order_type,
            expiration=expiration,
            direction_order=direction_order,
            amount=amount,
            triger_price=triger_price,
            leverage=leverage,
            limit_price=limit_price,
            stop_price=stop_price,
            stop_triger_price=stop_triger_price,
            take_triger_price=take_triger_price,
            position_size=position_size,
            direction_position=direction_position,
            margin=margin,
            open_notional=open_notional,
            last_updated_cumulative_premium=last_updated_cumulative_premium,
            fee=fee,
            discount=discount,
            rebate=rebate,
            last_updated_timestamp=last_updated_timestamp,
            oracle_price=oracle_price,
            spread=spread,
            oracle_timestamp=oracle_timestamp,
            asset_id=asset_id
        )
        logger.info(f"Adding Storm execute_order {execute_order}")
        db.serialize(execute_order)


class StormCompleteOrderParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj: dict) -> bool:
        return obj.get("opcode") == Parser.opcode_signed(0xcf90d618) and obj.get("direction") == "in"

    def handle_internal(self, obj: dict, db: DB):
        logger.info(f"Parsing storm complete_order message {Parser.require(obj.get('msg_hash'))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0xcf90d618

        order_type = cell.load_uint(4)
        order_index = cell.load_uint(3)
        direction = cell.load_uint(1)
        origin_op = cell.load_uint(32)
        oracle_price = cell.load_coins()

        position = cell.load_ref().begin_parse()
        """
        position#_ size:int128 direction:Direction 
        margin:Coins open_notional:Coins 
        last_updated_cumulative_premium:int64
        fee:uint32 discount:uint32 rebate:uint32 
        last_updated_timestamp:uint32 = PositionData
        """
        position_size = position.load_int(128)
        direction_position = position.load_uint(1)
        margin = position.load_coins()
        open_notional = position.load_coins()
        last_updated_cumulative_premium = position.load_int(64)
        fee = position.load_uint(32)
        discount = position.load_uint(32)
        rebate = position.load_uint(32)
        last_updated_timestamp = position.load_uint(32)

        amm_state = cell.load_ref().begin_parse()
        quote_asset_reserve = amm_state.load_coins()
        quote_asset_weight = amm_state.load_coins()
        base_asset_reserve = amm_state.load_coins()

        complete_order = StormCompleteOrder(
            tx_hash=Parser.require(obj.get("tx_hash")),
            msg_hash=Parser.require(obj.get("msg_hash")),
            trace_id=Parser.require(obj.get("trace_id")),
            utime=Parser.require(obj.get("created_at")),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash")))),
            order_type=order_type,
            order_index=order_index,
            direction=direction,
            origin_op=origin_op,
            oracle_price=oracle_price,
            position_size=position_size,
            direction_position=direction_position,
            margin=margin,
            open_notional=open_notional,
            last_updated_cumulative_premium=last_updated_cumulative_premium,
            fee=fee,
            discount=discount,
            rebate=rebate,
            last_updated_timestamp=last_updated_timestamp,
            quote_asset_reserve=quote_asset_reserve,
            quote_asset_weight=quote_asset_weight,
            base_asset_reserve=base_asset_reserve
        )
        logger.info(f"Adding Storm complete_order {complete_order}")
        db.serialize(complete_order)


class StormUpdatePositionParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj: dict) -> bool:
        return obj.get("opcode") == Parser.opcode_signed(0x60dfc677) and obj.get("direction") == "in"

    def handle_internal(self, obj: dict, db: DB):
        logger.info(f"Parsing storm update_position message {Parser.require(obj.get('msg_hash'))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0x60dfc677

        direction = cell.load_uint(1)
        origin_op = cell.load_uint(32)
        oracle_price = cell.load_coins()

        position = cell.load_ref().begin_parse()
        """
        position#_ size:int128 direction:Direction 
        margin:Coins open_notional:Coins 
        last_updated_cumulative_premium:int64
        fee:uint32 discount:uint32 rebate:uint32 
        last_updated_timestamp:uint32 = PositionData
        """
        position_size = position.load_int(128)
        direction_position = position.load_uint(1)
        margin = position.load_coins()
        open_notional = position.load_coins()
        last_updated_cumulative_premium = position.load_int(64)
        fee = position.load_uint(32)
        discount = position.load_uint(32)
        rebate = position.load_uint(32)
        last_updated_timestamp = position.load_uint(32)

        amm_state = cell.load_ref().begin_parse()
        quote_asset_reserve = amm_state.load_coins()
        quote_asset_weight = amm_state.load_coins()
        base_asset_reserve = amm_state.load_coins()

        update_position = StormUpdatePosition(
            tx_hash=Parser.require(obj.get("tx_hash")),
            msg_hash=Parser.require(obj.get("msg_hash")),
            trace_id=Parser.require(obj.get("trace_id")),
            utime=Parser.require(obj.get("created_at")),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash")))),
            direction=direction,
            origin_op=origin_op,
            oracle_price=oracle_price,
            stop_trigger_price=None,
            take_trigger_price=None,
            position_size=position_size,
            direction_position=direction_position,
            margin=margin,
            open_notional=open_notional,
            last_updated_cumulative_premium=last_updated_cumulative_premium,
            fee=fee,
            discount=discount,
            rebate=rebate,
            last_updated_timestamp=last_updated_timestamp,
            quote_asset_reserve=quote_asset_reserve,
            quote_asset_weight=quote_asset_weight,
            base_asset_reserve=base_asset_reserve
        )
        logger.info(f"Adding Storm update_position {update_position}")
        db.serialize(update_position)


class StormUpdateStopLossPositionParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj: dict) -> bool:
        return obj.get("opcode") == Parser.opcode_signed(0x5d1b17b8) and obj.get("direction") == "in"

    def handle_internal(self, obj: dict, db: DB):
        logger.info(f"Parsing storm update_position_stop_loss message {Parser.require(obj.get('msg_hash'))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0x5d1b17b8

        direction = cell.load_uint(1)
        stop_trigger_price = cell.load_coins()
        take_trigger_price = cell.load_coins()
        origin_op = cell.load_uint(32)
        oracle_price = cell.load_coins()

        position = cell.load_ref().begin_parse()
        """
        position#_ size:int128 direction:Direction 
        margin:Coins open_notional:Coins 
        last_updated_cumulative_premium:int64
        fee:uint32 discount:uint32 rebate:uint32 
        last_updated_timestamp:uint32 = PositionData
        """
        position_size = position.load_int(128)
        direction_position = position.load_uint(1)
        margin = position.load_coins()
        open_notional = position.load_coins()
        last_updated_cumulative_premium = position.load_int(64)
        fee = position.load_uint(32)
        discount = position.load_uint(32)
        rebate = position.load_uint(32)
        last_updated_timestamp = position.load_uint(32)

        amm_state = cell.load_ref().begin_parse()
        quote_asset_reserve = amm_state.load_coins()
        quote_asset_weight = amm_state.load_coins()
        base_asset_reserve = amm_state.load_coins()

        update_position = StormUpdatePosition(
            tx_hash=Parser.require(obj.get("tx_hash")),
            msg_hash=Parser.require(obj.get("msg_hash")),
            trace_id=Parser.require(obj.get("trace_id")),
            utime=Parser.require(obj.get("created_at")),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash")))),
            direction=direction,
            origin_op=origin_op,
            oracle_price=oracle_price,
            stop_trigger_price=stop_trigger_price,
            take_trigger_price=take_trigger_price,
            position_size=position_size,
            direction_position=direction_position,
            margin=margin,
            open_notional=open_notional,
            last_updated_cumulative_premium=last_updated_cumulative_premium,
            fee=fee,
            discount=discount,
            rebate=rebate,
            last_updated_timestamp=last_updated_timestamp,
            quote_asset_reserve=quote_asset_reserve,
            quote_asset_weight=quote_asset_weight,
            base_asset_reserve=base_asset_reserve
        )
        logger.info(f"Adding Storm update_position {update_position}")
        db.serialize(update_position)


class StormTradeNotificationParser(Parser):
    def topics(self):
        return [TOPIC_MESSAGES]

    def predicate(self, obj: dict) -> bool:
        return obj.get("opcode") == Parser.opcode_signed(0x3475fdd2) and obj.get("direction") == "in"

    def handle_internal(self, obj: dict, db: DB):
        logger.info(f"Parsing storm trade_notification message {Parser.require(obj.get('msg_hash'))}")
        cell = Parser.message_body(obj, db).begin_parse()
        cell.load_uint(32) # 0x3475fdd2

        asset_id = cell.load_uint(16)
        free_amount = cell.load_int(64)
        locked_amount = cell.load_int(64)
        exchange_amount = cell.load_int(64)
        withdraw_locked_amount = cell.load_uint(64)
        fee_to_stakers = cell.load_uint(64)
        withdraw_amount = cell.load_uint(64)
        trader_addr = cell.load_address()
        origin_addr = cell.load_address()

        referral_amount, referral_addr = None, None
        if cell.load_uint(1):
            referral = cell.load_ref().begin_parse()
            referral_amount = referral.load_coins()
            referral_addr = referral.load_address()

        trade_notification = StormTradeNotification(
            tx_hash=Parser.require(obj.get("tx_hash")),
            msg_hash=Parser.require(obj.get("msg_hash")),
            trace_id=Parser.require(obj.get("trace_id")),
            utime=Parser.require(obj.get("created_at")),
            successful=Parser.require(db.is_tx_successful(Parser.require(obj.get("tx_hash")))),
            asset_id=asset_id,
            free_amount=free_amount,
            locked_amount=locked_amount,
            exchange_amount=exchange_amount,
            withdraw_locked_amount=withdraw_locked_amount,
            fee_to_stakers=fee_to_stakers,
            withdraw_amount=withdraw_amount,
            trader_addr=trader_addr,
            origin_addr=origin_addr,
            referral_amount=referral_amount,
            referral_addr=referral_addr
        )
        logger.info(f"Adding Storm trade_notification {trade_notification}")
        db.serialize(trade_notification)
