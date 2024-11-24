-- initial script

CREATE TABLE parsed.mc_libraries (
	boc varchar NULL
);
CREATE UNIQUE INDEX mc_libraries_md5_idx ON parsed.mc_libraries USING btree (md5((boc)::text));


-- core prices

CREATE TABLE prices.core (
	tx_hash bpchar(44) NOT NULL,
	lt int8 NULL,
	asset varchar NOT NULL,
	price numeric NOT NULL,
	price_ts int8 NULL,
	created timestamp NULL,
	updated timestamp NULL,
	CONSTRAINT core_pkey PRIMARY KEY (tx_hash)
);
CREATE INDEX core_asset_idx ON prices.core USING btree (asset, price_ts DESC);

-- TON Hedge

CREATE TYPE public."ton_hedge_option_type" AS ENUM (
	'call',
	'put');

CREATE TABLE parsed.tonhedge_option (
    tx_hash bpchar(44) NULL primary key,
    trace_id bpchar(44) NULL,
    event_time int4 NULL,
    id numeric NULL
    option_type public."ton_hedge_option_type" NULL,
    option_price numeric NULL,
    opened_asset_price numeric NULL,
    strike_price numeric NULL,
    period numeric NULL,
    amount numeric NULL,
    purchased_at timestamp NULL,
    initial_holder varchar NULL,
    service_fee numeric NULL,
    permium numeric NULL,
    notional_volume numeric NULL,
    volume numeric NULL
);

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

CREATE TABLE parsed.jetton_mint (
    tx_hash bpchar(44) NULL primary key,
    msg_hash bpchar(44) NULL,
    trace_id bpchar(44) NULL,
    utime int4 NULL,
    successful boolean NULL,
    query_id numeric NULL,
    amount numeric NULL,
    minter varchar NULL,
    from_address varchar NULL,
    wallet varchar NULL,
    response_destination varchar NULL,
    forward_ton_amount numeric NULL,
    forward_payload bytea NULL,
    created timestamp NULL,
    updated timestamp NULL
);

ALTER TABLE parsed.jetton_mint ADD column if not exists "owner" varchar NULL;
ALTER TABLE parsed.jetton_mint ADD column if not exists "jetton_master_address" varchar NULL;

--  required for fast lookup of parent message by msg_hash
CREATE INDEX trace_edges_msg_hash_idx ON public.trace_edges (msg_hash);

-- to be aligned with jetton_transfers and jetton_burn
ALTER TABLE parsed.jetton_mint ADD tx_lt int8 NULL;

CREATE TABLE parsed.jetton_metadata (
    address public."tonaddr" not NULL primary key,
    update_time_onchain int4 null, -- onchain
    update_time_metadata int4 null, -- metadata update time
    mintable bool NULL, -- from onchain
  	admin_address public."tonaddr" NULL, -- from onchain
    jetton_content_onchain jsonb NULL, -- onchain
  	jetton_wallet_code_hash public."tonhash" NULL, -- onchain
	code_hash public."tonhash" null, -- onchain
	metadata_status int, -- 1 - ok, -1 error, 0 on chain only
	symbol varchar null, -- on/offchain
	name varchar null, -- on/offchain
	description varchar null, -- on/offchain
	image varchar null, -- on/offchain
	image_data varchar null, -- on/offchain
	decimals smallint null, -- on/offchain
	sources varchar null, -- [on|off] 6 times for symbol, name, description, image, image_data, decimals
	tonapi_image_url varchar null -- tonapi image url
);

-- megaton dex support
ALTER TYPE public.dex_name ADD VALUE 'megaton' AFTER 'ston.fi_v2';

-- required for megaton parser
CREATE INDEX jetton_transfers_trace_id_idx ON public.jetton_transfers (trace_id);

-- TonFun
CREATE TABLE parsed.tonfun_bcl_trade (
    tx_hash bpchar(44) NULL primary key,
    trace_id bpchar(44) NULL,
    event_time int4 NULL,
    bcl_master varchar NULL,
    event_type varchar NULL,
    trader_address varchar null,
    ton_amount numeric NULL,
    bcl_amount numeric NULL,
    referral_ver int8 NULL,
    partner_address varchar NULL,
    platform_tag varchar NULL,
    extra_tag varchar NULL,
    created timestamp NULL,
    updated timestamp NULL
);

