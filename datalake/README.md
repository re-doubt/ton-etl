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
URL: **s3://ton-blockchain-public-datalake/v1/transactions/**

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


## Jettons

TBD

## DEX Swaps

TBD

