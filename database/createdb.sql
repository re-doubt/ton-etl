-- initial script

-- Tradoor

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