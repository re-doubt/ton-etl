#!/usr/bin/env python

from datetime import datetime, timezone
import hashlib
import os
from tqdm import tqdm
import time
import json
import traceback
from typing import Dict
from loguru import logger
from kafka import KafkaConsumer
import boto3
import avro.schema
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader

AVRO_TMP_BUFFER = "tmp_buffer.avro"
FLUSH_INTERVAL = 1000

class Partition:
    def __init__(self, partition, schema):
        self.partition = partition
        self.count = 0
        self.filename = f"{partition}.avro"
        if os.path.exists(self.filename):
            logger.info(f"Removing {self.filename}")
            os.remove(self.filename)
        self.writer = DataFileWriter(open(self.filename, "wb"), DatumWriter(), schema)
        self.file_size = 0

    def __del__(self):
        self.writer.close()
        os.remove(self.filename)

    def append(self, obj):
        self.writer.append(obj)
        self.count += 1
        self.last_event_ts = int(time.time())
        if self.count % FLUSH_INTERVAL == 0:
            self.writer.flush()
                
        self.file_size = os.path.getsize(self.filename)

    def flush(self, s3, destination_s3_bucket, destination_s3_prefix, destination_s3_suffix):
        self.writer.flush()
        self.writer.close()
        self.file_size = os.path.getsize(self.filename)
        with open(self.filename, "rb") as f:
            hash_key = hashlib.sha256(f.read()).hexdigest()[0:24]
        path = f"{destination_s3_prefix}/block_date={self.partition}/{hash_key}_{destination_s3_suffix}.avro"
        logger.info(f"Uploading {self.file_size} bytes to {path}")
        s3.upload_file(self.filename, destination_s3_bucket, path)

def repartition(source_s3_bucket, source_s3_prefix, destination_s3_bucket, destination_s3_prefix, destination_s3_suffix,
                 field, max_partition_size):
    s3 = boto3.client('s3')
    continuation_token = None
    files = 0
    partitions: Dict[str, Partition] = {}
    while True:
        opts = {}
        if continuation_token:
            opts['ContinuationToken'] = continuation_token
        objects = s3.list_objects_v2(Bucket=source_s3_bucket, Prefix=source_s3_prefix, MaxKeys=100, **opts)
        for obj in objects.get('Contents', []):
            files += 1
            key = obj['Key']
            logger.info(f"Processing {key}")
            if os.path.exists(AVRO_TMP_BUFFER):
                logger.info(f"Removing {AVRO_TMP_BUFFER}")
                os.remove(AVRO_TMP_BUFFER)
            obj = s3.download_file(Bucket=source_s3_bucket, Key=key, Filename=AVRO_TMP_BUFFER)
            with open(AVRO_TMP_BUFFER, "rb") as f:
                reader = DataFileReader(f, DatumReader())
                schema = avro.schema.parse(reader.schema)
                for record in tqdm(reader):
                    # logger.info(record)
                    timestamp = record[field]
                    partition_key = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y%m%d')
                    if partition_key not in partitions:
                        logger.info(f"Creating partition {partition_key}")
                        # logger.info(reader.schema)
                        partitions[partition_key] = Partition(partition_key, schema)
                    partitions[partition_key].append(record)
                    flushed = set()
                    for partition in partitions.values():
                        # logger.info(f"Partition {partition.partition} has {partition.count} records, {partition.file_size} bytes")
                        if partition.file_size > max_partition_size:
                            logger.info(f"Partition {partition.partition} has reached max size {max_partition_size}, flushing")
                            flushed.add(partition.partition)
                            partition.flush(s3, destination_s3_bucket, destination_s3_prefix, destination_s3_suffix)
                    for partition in flushed:
                        del partitions[partition]

        if objects.get('IsTruncated', False):
            continuation_token = objects.get('NextContinuationToken')
            logger.info(f"Continuing with next page")
        else:
            logger.info(f"Done, processed {files} files")
            break

    for partition in partitions.values():
        logger.info(f"Partition {partition.partition} has {partition.count} records, {partition.file_size} bytes, flusing")
        partition.flush(s3, destination_s3_bucket, destination_s3_prefix, destination_s3_suffix)

if __name__ == "__main__":
    repartition(os.environ.get("SOURCE_S3_BUCKET"), os.environ.get("SOURCE_S3_PREFIX"), 
                os.environ.get("DESTINATION_S3_BUCKET"), os.environ.get("DESTINATION_S3_PREFIX"),
                os.environ.get("DESTINATION_S3_SUFFIX"),
                os.environ.get("PARTITION_FIELD"),
                os.environ.get("MAX_PARTITION_SIZE", 100000000))
    

