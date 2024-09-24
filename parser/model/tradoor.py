from dataclasses import dataclass
import decimal

"""
CREATE TABLE parsed.tradoor_perp_order (
	tx_hash bpchar(44) NULL primary key,
	trace_id bpchar(44) NULL,
    event_time int4 NULL,
	op_type int4 NULL,
    token_id int4 NULL,
	address varchar NULL,
    is_long boolean NULL,
	margin_delta numeric NULL,
    size_delta numeric NULL,
    trigger_price numeric NULL,
    trigger_above boolean NULL,
    execution_fee numeric NULL,
    order_id numeric NULL,
    trx_id numeric NULL,
    request_time int4 NULL,
    created timestamp NULL,
    updated timestamp NULL
);
"""

@dataclass
class TradoorPerpOrderEvent:
    __tablename__ = 'tradoor_perp_order'

    tx_hash: str
    trace_id: str
    event_time: int
    op_type: int
    token_id: int
    address: str
    is_long: bool
    margin_delta: decimal.Decimal
    size_delta: decimal.Decimal
    trigger_price: decimal.Decimal
    trigger_above: bool
    execution_fee: decimal.Decimal
    order_id: decimal.Decimal
    trx_id: decimal.Decimal
    request_time: int
