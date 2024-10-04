# Datalake exporters

Datalake exporters are responsible for exporting data from Kafka to S3. It converts messages to Avro format, 
apply additional transformations and uploads them to S3.

## Messages exporter

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

## Jetton transfers exporter

[AVRO schema](./schemas/jetton_transfers.avsc)

Additional to standard fields we are adding comment field from forward_payload (if it is present).

## Jetton burns exporter

[AVRO schema](./schemas/jetton_burns.avsc)

## DEX Swaps exporter

[AVRO schema](./schemas/dex_swaps.avsc)

Note that some fields are supported not for all DEXes:
* reserver0 and reserve1 - only for DeDust
* min_out and query_id - only for Ston.fi and Ston.fi V2

Volume in USD and TON is caluldated only for swaps with TON, USDT or staked TON.

## NFT transfers exporter

[AVRO schema](./schemas/nft_transfers.avsc)

Additional to standard fields we are adding comment field from forward_payload (if it is present).

## GasPump trades exporter

[AVRO schema](./schemas/gaspump_trades.avsc)

## Blocks exporter

[AVRO schema](./schemas/blocks.avsc)
