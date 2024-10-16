# Datalake exporters

Datalake exporters are responsible for exporting data from Kafka to cloud storage. It converts messages to Avro format, apply additional transformations and uploads them to S3.

Datalake locations:
* Test environment: s3://ton-blockchain-public-datalake-test/v5/
* Production environment: s3://ton-blockchain-public-datalake/v1/

All data types are stored in separate folders and named by type. Data is partitioned by block date.
Initially data is partitioned by adding date, but at the end of the day it is re-partitioned using [this script](./repartition.py).

# Data types

## Blocks

[AVRO schema](./schemas/blocks.avsc)

Contains information about blocks (masterchain and workchains).
Partition field: __gen_utime__

## Transactions

[AVRO schema](./schemas/transactions.avsc).

Additionaly we are adding account_state_code_hash_after and account_state_balance_after fields.

## Messages

[AVRO schema](./schemas/messages.avsc)
Message body is stored separately in message_contents table and is not accessible immidiately during 
Kafka message handling. So we are fetching message_content from DB and also extracting 
text comment if message has it.
Also for external in messages we are adding created_at from corresponding transactions.
According to the standard external in message has no [created_at field](https://github.com/ton-blockchain/ton/blob/921aa29eb54db42de21e0f89610c347670988ed1/crypto/block/block.tlb#L129):
```
ext_in_msg_info$10 src:MsgAddressExt dest:MsgAddressInt 
  import_fee:Grams = CommonMsgInfo;
```
But from analytical perspective it is useful to have this field.