#!/usr/bin/env python

from datetime import datetime
import os
import time
import json
import traceback
from loguru import logger
from kafka import KafkaConsumer
import boto3
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from converters.messages import MessageConverter
from converters.jetton_transfers import JettonTransfersConverter
from converters.blocks import BlocksConverter
from converters.jetton_burns import JettonBurnsConverter
from converters.nft_transfers import NftTransfersConverter
from converters.dex_swaps import DexSwapsConverter
from converters.gaspump import GasPumpConverter
from converters.agg_prices import AggPricesConverter
from converters.tradoor_position_change import TradoorPositionChangeConverter


AVRO_TMP_BUFFER = "tmp_buffer.avro"

CONVERTERS = {
    "messages": MessageConverter(),
    "jetton_transfers": JettonTransfersConverter(),
    "jetton_burns": JettonBurnsConverter(),
    "blocks": BlocksConverter(),
    "nft_transfers": NftTransfersConverter(),
    "dex_swaps": DexSwapsConverter(),
    "gaspump_trades": GasPumpConverter(),
    "agg_prices": AggPricesConverter(),
    "tradoor_position_change": TradoorPositionChangeConverter()
}

if __name__ == "__main__":
    group_id = os.environ.get("KAFKA_GROUP_ID")
    topic = os.environ.get("KAFKA_TOPIC", "ton.public.messages")
    converter_name = os.environ.get("CONVERTER", "messages")
    assert converter_name in CONVERTERS, f"Converter {converter_name} not found"
    converter = CONVERTERS[converter_name]

    max_file_size = int(os.environ.get("MAX_FILE_SIZE", '100000000'))
    log_interval = int(os.environ.get("LOG_INTERVAL", '10'))

    # We should commit after commit_interval
    commit_interval = int(os.environ.get("COMMIT_INTERVAL", '7200'))
    # But only if we have at least min_commit_size in the buffer
    min_commit_size = int(os.environ.get("MIN_COMMIT_SIZE", '1000000'))

    datalake_s3_bucket = os.environ.get("DATALAKE_S3_BUCKET")
    datalake_s3_prefix = os.environ.get("DATALAKE_S3_PREFIX")


    FIELDS_TO_REMOVE = ['__op', '__table', '__source_ts_ms']

    consumer = KafkaConsumer(
            group_id=group_id,
            bootstrap_servers=os.environ.get("KAFKA_BROKER"),
            auto_offset_reset=os.environ.get("KAFKA_OFFSET_RESET", 'earliest'),
            enable_auto_commit=False
            )

    logger.info(f"Subscribing to {topic}")
    consumer.subscribe(topic)

    last = time.time()
    last_commit = time.time()
    total = 0
    writer = None
    count = 0
    s3 = boto3.client('s3')

    for msg in consumer:
        try:
            total += 1
            obj = json.loads(msg.value.decode("utf-8"))
            __op = obj.get('__op', None)
            if not (__op == 'c' or __op == 'r'): # ignore everything apart from new items (c - new item, r - initial snapshot)
                continue

            if writer is None:
                writer = DataFileWriter(open(AVRO_TMP_BUFFER, "wb"), DatumWriter(), converter.schema)
            for f in FIELDS_TO_REMOVE:
                del obj[f]
            obj['__id'] = f"{msg.partition}_{msg.offset}_{msg.timestamp}"
            if converter.strict:
                writer.append(converter.convert(obj))
            else:
                try:
                    writer.append(converter.convert(obj))
                except Exception as e:
                    logger.error(f"Failed to convert item {obj}: {e} {traceback.format_exc()}")
                    continue
            count += 1
            writer.flush() # TODO optimize and avoid flushing after every message
            file_size = os.path.getsize(AVRO_TMP_BUFFER)
            if file_size > max_file_size or (time.time() - last_commit > commit_interval and file_size > min_commit_size):
                writer.close()
                # TODO use object timestamp for partition
                partition = datetime.now().strftime('%Y%m%d')
                path = f"{datalake_s3_prefix}{converter.name()}/upload_date={partition}/{msg.partition}_{msg.offset}_{msg.timestamp}.avro"
                logger.info(f"Going to flush file, total size is {file_size}B, {time.time() - last_commit:0.1f}s since last commit, {count} items to {path}")

                s3.upload_file(AVRO_TMP_BUFFER, datalake_s3_bucket, path)
                writer = None
                now = time.time()
                last_commit = time.time()
                logger.info(f"{1.0 * total / (now - last):0.2f} Kafka messages per second")
                last = now
                total = 0
                consumer.commit()
                
        except Exception as e:
            logger.error(f"Failted to process item {msg}: {e} {traceback.format_exc()}")
            raise
        # if db.updated >= commit_batch_size:
        #     logger.info(f"Reached {db.updated} DB updates, making commit")
        #     db.release() # commit release connection
        #     consumer.commit() # commit kafka offset
        #     db.acquire() # acquire a new connection
