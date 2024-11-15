# Datalake exporters

Datalake exporters are responsible for exporting data from Kafka to cloud storage. It converts messages to Avro format, apply additional transformations and uploads them to S3.

Datalake locations:
* Production environment: s3://ton-blockchain-public-datalake/v1/

All data types are stored in separate folders and named by type. Data is partitioned by block date. Block date
is extracted from specific field for each data type and converted into string in __YYYYMMDD__ format.
Initially data is partitioned by adding date, but at the end of the day it is re-partitioned using [this script](./repartition.py).

# Data types

## Blocks

[AVRO schema](./schemas/blocks_export.avsc)

Partition field: __gen_utime__
URL: **s3://ton-blockchain-public-datalake/v1/blocks/**

Contains information about blocks (masterchain and workchains).

## Transactions

[AVRO schema](./schemas/transactions_export.avsc).

Partition field: __now__
URL: **s3://ton-blockchain-public-datalake/v1/blocks/**

Additionaly we are adding account_state_code_hash_after and account_state_balance_after fields.

## Messages

[AVRO schema](./schemas/messages_export.avsc)

Partition field: __tx_now__
URL: **s3://ton-blockchain-public-datalake/v1/messages/**

Contains messages from transactions. Internal messages are included twice with different direction:
* in - message that initiated transaction
* out - message that was result of transaction


## Messages with raw bodies

[AVRO schema](./schemas/messages_with_body_export.avsc)

Partition field: __tx_now__
URL: **s3://ton-blockchain-public-datalake/v1/messages_with_body/**

Contains the same data as ``messages`` table with two more fields:
* body_boc - raw body of the message body
* init_state_boc - raw init state (if present) from the message

## Account states

[AVRO schema](./schemas/account_states.avsc)

Partition field: __timestamp__
URL: **s3://ton-blockchain-public-datalake/v1/account_states/**

Contains raw account states with raw data and code.


## Jetton events

[AVRO schema](./schemas/jetton_events_export.avsc)

Partition field: __utime__
URL: **s3://ton-blockchain-public-datalake/v1/jetton_events/**

Contains jetton events, event type is defined in ``type`` field:
* transfer - TEP-74 transfer event
* burn - TEP-74 burn event
* mint - TEP-74 jetton standard does not specify mint format but it has recommended form of internal_transfer message. 
So we are using it as mint event. Also there are some jetton-specific mint implementations, 
the current implementation supports HIPO hTON mints.

All jetton events include tx_aborted field, pay attention that if it is ``false`` then the event should be discarded.
Aborted events are stored becase it could be useful for some types of analysis.

``source`` field is set to ``null`` for mint events and ``destination`` is set to ``null`` for burn events.

Note that fields ``query_id``, ``forward_ton_amount``, ``amount`` are stored as  decimal values with scale equals to 0. Since the data mart
doesn't support off-chain metadata and stores only raw data the amount is stored as raw value without dividing by 10^decimals.

## Jetton metadata

[AVRO schema](./schemas/jetton_metadata.avsc)

Partition field: __adding_at__
URL: **s3://ton-blockchain-public-datalake/v1/jetton_metadata/**

According to [TEP-64](https://github.com/ton-blockchain/TEPs/blob/master/text/0064-token-data-standard.md)
standard Jetton metadata could be stored off-chain or on-chain (or even both). Having in mind that the data could be
stored off-chain and may not be available at the time of processing we are using the following approach:
* Get on-chain metadata
* If off-chain metadata is available and the field is present, store value from off-chain metadata
* If off-chain metadata is not available, fallback to [tonapi API V2](https://tonapi.io/api-v2#operations-Jettons-getJettonInfo)
to extract jetton metadata cached by tonapi.

Also for all jettons cached image from tonapi is requested. It is a mitigation for the case when image is not available 
any longer.

Fields description:
* address - jetton master address
* update_time_onchain - time of on-chain update (for example in case of admin address transfer)
* update_time_metadata - time of off-chain update
* mintable - mintable flag (on-chain value)
* admin_address - admin address (on-chain value)
* jetton_content_onchain - JSON serialized into string with on-chain jetton content
* jetton_wallet_code_hash - jetton wallet code_hash (on-chain value)
* code_hash - jetton code hash (on-chain value)
* metadata_status - off-chain metadata update status (0 - no off-chain metadata, 1 - success, -1 - error)
* symbol - TEP-64 jetton symbol (on-chain or off-chain value, see sources field for details)
* name - TEP-64 jetton name (on-chain or off-chain value, see sources field for details)
* description - TEP-64 jetton description (on-chain or off-chain value, see sources field for details)
* image - TEP-64 jetton image url (on-chain or off-chain value, see sources field for details)
* image_data - TEP-64 jetton image data (on-chain or off-chain value, see sources field for details)
* decimals - TEP-64 jetton decimals (on-chain or off-chain value, see sources field for details). Note that if decimals fields is not present it means that the jetton uses default value of 9.
* sources - recored with sources of jetton metadata fields (6 fields for symbol, name, description, image, image_data, decimals). Possible values are:
    * "" - field is not set
    * "onchain" - field is based on on-chain value
    * "offchain" - field is based on off-chain value
    * "tonapi" - tonapi was used to get the value (fallback)
* tonapi_image_url - tonapi cached image url
* adding_date - partition field, date when the output file was created

## Jetton metadata snapshots

``jetton_metadata`` table allows to get the full history of jetton metadata changes but for most cases it is more suitable to have
the latest snapshot of jetton metadata. To simplify usage in this case daily snapshots with the latest metadata are created.

Partition field: __snapshot_date__
URL: **s3://ton-blockchain-public-datalake/v1/jetton_metadata_snapshots/**

This table contains the same data as ``jetton_metadata`` table but only for the latest snapshot for each jetton.

Note: for performance reasons daily snapshots are splited into 10 files.

It is recommended to use ``jetton_metadata_latest`` view to get the latest snapshot of jetton metadata (see [athena_ddl.sql](./athena_ddl.sql)).


## DEX Swaps

TBD


# Integration with Athena

As far the data is stored in S3 in Avro format Athena can directly read it. To start working with the data you need to create table with the DDL
provided in [athena_ddl.sql](./athena_ddl.sql) file and load partitions using ``MSCK REPAIR TABLE`` command.

## Query examples

Get most active jettons from the last 30 days:

```sql
with top_jettons as (
select jetton_master, approx_distinct(trace_id) operations from jetton_events
where block_date >= date_format(date_add('day', -30, current_date), '%Y%m%d')
group by 1
order by operations desc limit 10
)
select symbol, jetton_master, operations from top_jettons 
join jetton_metadata_latest on jetton_master = address
order by operations desc
```