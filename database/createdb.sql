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

CREATE TABLE parsed.tradoor_perp_position_change (
    tx_hash bpchar(44) NULL primary key,
    trace_id bpchar(44) NULL,
    event_time int4 NULL,
    trx_id numeric NULL,
    order_id numeric NULL,
    op_type int4 NULL,
    position_id numeric NULL,
    address varchar NULL,
    token_id int4 NULL,
    is_long boolean NULL,
    margin_delta numeric NULL,
    margin_after numeric NULL,
    size_delta numeric NULL,
    size_after numeric NULL,
    trade_price numeric NULL,
    trigger_price numeric NULL,
    entry_price numeric NULL,
    funding_fee numeric NULL,
    rollover_fee numeric NULL,
    trading_fee numeric NULL,
    created timestamp NULL,
    updated timestamp NULL
);


CREATE TABLE parsed.tradoor_option_order (
    tx_hash bpchar(44) NULL primary key,
    trace_id bpchar(44) NULL,
    event_time int4 NULL,
    address varchar NULL,
    token_id int8 NULL,
    client_order_id numeric NULL,
    is_call boolean NULL,
    order_time int4 NULL,
    option_interval int4 NULL,
    strike_price numeric NULL,
    option_price numeric NULL,
    quantity numeric NULL,
    trigger_price numeric NULL,
    option_fee numeric NULL,
    execution_fee numeric NULL,
    is_executed boolean NULL,
    order_id numeric NULL,
    trx_id numeric NULL,
    ts int4 NULL,
    created timestamp NULL,
    updated timestamp NULL
);

-- GasPump events

create type parsed.gaspump_event as enum('DeployAndBuyEmitEvent', 'BuyEmitEvent', 'SellEmitEvent');

CREATE TABLE parsed.gaspump_trade (
    tx_hash bpchar(44) NULL primary key,
    trace_id bpchar(44) NULL,
    event_time int4 NULL,
    jetton_master varchar NULL,
    event_type parsed.gaspump_event  NULL,
    trader_address varchar null,
    ton_amount numeric NULL,
    jetton_amount numeric NULL,
    fee_ton_amount numeric NULL,
    input_ton_amount numeric NULL,
    bonding_curve_overflow bool NULL,
    created timestamp NULL,
    updated timestamp NULL
);
