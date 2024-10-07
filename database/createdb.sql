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
    is_increased boolean NULL,
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


-- DEX Swaps
CREATE TYPE public."dex_name" AS ENUM (
	'dedust',
	'ston.fi');

CREATE TABLE parsed.dex_swap_parsed (
	tx_hash bpchar(44) NULL,
	msg_hash bpchar(44) NOT NULL,
	trace_id bpchar(44) NULL,
	platform public."dex_name" NULL,
	swap_utime int8 NULL,
	swap_user varchar NULL,
	swap_pool varchar NULL,
	swap_src_token varchar NULL,
	swap_dst_token varchar NULL,
	swap_src_amount numeric NULL,
	swap_dst_amount numeric NULL,
	referral_address varchar NULL,
	reserve0 numeric NULL,
	reserve1 numeric NULL,
	query_id numeric NULL,
	min_out numeric NULL,
	volume_usd numeric NULL,
	volume_ton numeric NULL,
	created timestamp NULL,
	updated timestamp NULL,
	CONSTRAINT dex_swap_parsed_pkey PRIMARY KEY (msg_hash)
);
CREATE INDEX dex_swap_parsed_swap_utime_idx ON parsed.dex_swap_parsed USING btree (swap_utime);
CREATE INDEX dex_swap_parsed_tx_hash_idx ON parsed.dex_swap_parsed USING btree (tx_hash);

-- ston.fi V2 support
ALTER TYPE public.dex_name ADD VALUE 'ston.fi_v2' AFTER 'ston.fi';
ALTER TABLE parsed.dex_swap_parsed ADD column if not exists router varchar NULL;

-- EVAA

CREATE TABLE parsed.evaa_supply (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    query_id numeric NULL,
    amount numeric NULL,
    asset_id varchar NULL,
    owner_address varchar NULL,
    repay_amount_principal numeric NULL,
    supply_amount_principal numeric NULL,
    created timestamp NULL,
    updated timestamp NULL
);

CREATE TABLE parsed.evaa_withdraw (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    query_id numeric NULL,
    amount numeric NULL,
    asset_id varchar NULL,
    owner_address varchar NULL,
    borrow_amount_principal numeric NULL,
    reclaim_amount_principal numeric NULL,
    recipient_address varchar NULL,
    approved boolean NULL,
    created timestamp NULL,
    updated timestamp NULL
);

CREATE TABLE parsed.evaa_liquidation (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    query_id numeric NULL,
    amount numeric NULL,
    protocol_gift numeric NULL,
    collateral_reward numeric NULL,
    min_collateral_amount numeric NULL,
    transferred_asset_id varchar NULL,
    collateral_asset_id varchar NULL,
    owner_address varchar NULL,
    liquidator_address varchar NULL,
    delta_loan_principal numeric NULL,
    delta_collateral_principal numeric NULL,
    new_user_loan_principal numeric NULL,
    new_user_collateral_principal numeric NULL,
    approved boolean NULL,
    created timestamp NULL,
    updated timestamp NULL
);

ALTER TABLE parsed.evaa_supply ADD column if not exists user_new_principal numeric NULL;

ALTER TABLE parsed.evaa_withdraw ADD column if not exists user_new_principal numeric NULL;

ALTER TABLE parsed.evaa_supply ADD column if not exists pool_address varchar NULL;

ALTER TABLE parsed.evaa_withdraw ADD column if not exists pool_address varchar NULL;

ALTER TABLE parsed.evaa_liquidation ADD column if not exists pool_address varchar NULL;

-- Jetton wallet balances

CREATE TABLE parsed.jetton_wallet_balances (
    address varchar NULL,
    tx_lt int8 NULL,
    jetton_master varchar NULL,
    owner varchar NULL,
    balance numeric NULL,
    created timestamp NULL,
    updated timestamp NULL,
    PRIMARY KEY(address, tx_lt)
);

-- Storm Trade

CREATE TABLE parsed.storm_execute_order (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    direction int2 NULL,
    order_index int2 NULL,
    trader_addr varchar NULL,
    prev_addr varchar NULL,
    ref_addr varchar NULL,
    executor_index int8 NULL,
    order_type int2 NULL,
    expiration int8 NULL,
    direction_order int2 NULL,
    amount numeric NULL,
    triger_price numeric NULL,
    leverage numeric NULL,
    limit_price numeric NULL,
    stop_price numeric NULL,
    stop_triger_price numeric NULL,
    take_triger_price numeric NULL,
    position_size numeric NULL,
    direction_position int2 NULL,
    margin numeric NULL,
    open_notional numeric NULL,
    last_updated_cumulative_premium numeric NULL,
    fee int8 NULL,
    discount int8 NULL,
    rebate int8 NULL,
    last_updated_timestamp int8 NULL,
    oracle_price numeric NULL,
    spread numeric NULL,
    oracle_timestamp int8 NULL,
    asset_id int8 NULL,
    created timestamp NULL,
    updated timestamp NULL
);

CREATE TABLE parsed.storm_complete_order (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    order_type int2 NULL,
    order_index int2 NULL,
    direction int2 NULL,
    origin_op int8 NULL,
    oracle_price numeric NULL,
    position_size numeric NULL,
    direction_position int2 NULL,
    margin numeric NULL,
    open_notional numeric NULL,
    last_updated_cumulative_premium numeric NULL,
    fee int8 NULL,
    discount int8 NULL,
    rebate int8 NULL,
    last_updated_timestamp int8 NULL,
    quote_asset_reserve numeric NULL,
    quote_asset_weight numeric NULL,
    base_asset_reserve numeric NULL,
    created timestamp NULL,
    updated timestamp NULL
);

CREATE TABLE parsed.storm_update_position (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    direction int2 NULL,
    origin_op int8 NULL,
    oracle_price numeric NULL,
    stop_trigger_price numeric NULL,
    take_trigger_price numeric NULL,
    position_size numeric NULL,
    direction_position int2 NULL,
    margin numeric NULL,
    open_notional numeric NULL,
    last_updated_cumulative_premium numeric NULL,
    fee int8 NULL,
    discount int8 NULL,
    rebate int8 NULL,
    last_updated_timestamp int8 NULL,
    quote_asset_reserve numeric NULL,
    quote_asset_weight numeric NULL,
    base_asset_reserve numeric NULL,
    created timestamp NULL,
    updated timestamp NULL
);

CREATE TABLE parsed.storm_trade_notification (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    asset_id int8 NULL,
    free_amount numeric NULL,
    locked_amount numeric NULL,
    exchange_amount numeric NULL,
    withdraw_locked_amount numeric NULL,
    fee_to_stakers numeric NULL,
    withdraw_amount numeric NULL,
    trader_addr varchar NULL,
    origin_addr varchar NULL,
    referral_amount numeric NULL,
    referral_addr varchar NULL,
    created timestamp NULL,
    updated timestamp NULL
);
