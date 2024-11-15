#!/usr/bin/env python

import os
import sys
import time
from typing import Dict
import uuid
from loguru import logger
import boto3
import botocore
from datetime import datetime, timedelta



if __name__ == "__main__":
    source_database = os.environ.get("SOURCE_DATABASE")
    target_database = os.environ.get("TARGET_DATABASE")
    source_table = os.environ.get("SOURCE_TABLE")
    target_table = os.environ.get("TARGET_TABLE")
    table_location = os.environ.get("TARGET_TABLE_LOCATION")
    tmp_location = os.environ.get("TMP_LOCATION")
    workgroup = os.environ.get("ATHENA_WORKGROUP")
    buckets_count = int(os.environ.get("BUCKETS_COUNT", 10))

    athena = boto3.client("athena", region_name="us-east-1")

    def execute_athena_query(query, database=source_database):
        response = athena.start_query_execution(QueryString=query,
                                                QueryExecutionContext={"Database": database},
                                                WorkGroup=workgroup)
        query_id = response['QueryExecutionId']
        while True:
            response = athena.get_query_execution(QueryExecutionId=query_id)
            if response['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                break
            time.sleep(5)
            logger.info(f"Query {query_id} is still running: {response['QueryExecution']['Status']['State']}")

    logger.info(f"Preparing source table {source_database}.{source_table}")
    execute_athena_query(f"MSCK REPAIR TABLE {source_table}", database=source_database)

    logger.info(f"Repartitioning table {source_database}.{source_table} => {target_database}.{target_table} ")

    glue = boto3.client("glue", region_name="us-east-1")
    source_table_meta = glue.get_table(DatabaseName=source_database, Name=source_table)
    logger.info(source_table_meta)
    
    try:
        target_table_meta = glue.get_table(DatabaseName=target_database, Name=target_table)
    except Exception as e:
        if e.__class__.__name__ != "EntityNotFoundException":
            raise e
        logger.warning(f"Table {target_table} not found in database {target_database}, creating new table")
        
        response =glue.create_table(
            DatabaseName=target_database,
            TableInput={
                "Name": target_table,
                "TableType": "EXTERNAL_TABLE",
                "StorageDescriptor": {
                    'Columns': [c for c in source_table_meta['Table']['StorageDescriptor']['Columns'] if c['Name'] != 'adding_date'],  
                    'Location': table_location,
                    'InputFormat': 'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat',
                    'SerdeInfo': source_table_meta['Table']['StorageDescriptor']['SerdeInfo'],
                },
                "PartitionKeys": [
                    {
                        "Name": "snapshot_date",
                        "Type": "string",
                    }
                ],
                "TableType": "EXTERNAL_TABLE",
            }
        )
        logger.info(response)
        target_table_meta = glue.get_table(DatabaseName=target_database, Name=target_table)
    
    tmp_table_name = f"{target_table}_increment_{str(uuid.uuid4()).replace('-', '')}"
    tmp_table_location = f"{tmp_location}/{tmp_table_name}"
    FIELDS = ", ".join([col['Name'] for col in source_table_meta['Table']['StorageDescriptor']['Columns']])
    sql = f"""
    create table "{source_database}".{tmp_table_name}
    with (
        format = 'AVRO', 
        write_compression = 'SNAPPY',
        external_location = '{tmp_table_location}',
        bucketed_by = ARRAY['address'],
        bucket_count = {buckets_count},
        partitioned_by = ARRAY['snapshot_date']
    )
    as
    with ranks as (
    SELECT address, update_time_onchain,
    update_time_metadata, mintable, admin_address, jetton_content_onchain,
    jetton_wallet_code_hash, code_hash, metadata_status, symbol,
    name, description, image, image_data, decimals, sources, tonapi_image_url,
    row_number() over (partition by address order by update_time_metadata desc, update_time_onchain desc) as rank FROM "{source_database}".{source_table}
    )
    select address, update_time_onchain, update_time_metadata, mintable, admin_address, 
    jetton_content_onchain, jetton_wallet_code_hash, code_hash, metadata_status, symbol, 
    name, description, image, image_data, decimals, sources, tonapi_image_url, 
    date_format(current_date, '%Y%m%d') as snapshot_date from ranks
    where rank = 1
    """
    logger.info(f"Running SQL code to convert data into single file dataset {sql}")


    execute_athena_query(sql)

    glue.delete_table(DatabaseName=source_database, Name=tmp_table_name)
    logger.info(f"Time to transfer output data from {tmp_table_location} to {table_location}")
    s3 = boto3.client("s3")
    # tmp_table_location = "s3://tf-analytcs-athena-output/tmp_repartition_space/blocks_increment_20241014_29c9c4a3e5aa4b019b1d8a6f9c6fb731"
    bucket, key = tmp_table_location.replace("s3://", "").split("/", 1)
    target_bucket, target_key = table_location.replace("s3://", "").split("/", 1)
    continuation_token = None
    while True:
        opts = {}
        if continuation_token:
            opts["ContinuationToken"] = continuation_token
        # TODO add suffix to key
        objects = s3.list_objects_v2(Bucket=bucket, Prefix=key, MaxKeys=100, **opts)
        for obj in objects.get("Contents", []):
            logger.info(f"Processing {obj['Key']}")
            suffix = "/".join(obj['Key'].split("/")[-2:])
            logger.info(f"Copying {obj['Key']} to {target_bucket}/{target_key}/{suffix}")
            # s3.copy_object(Bucket=target_bucket, CopySource=f"{bucket}/{obj['Key']}", Key=f"{target_key}/{suffix}")
            s3.copy({'Bucket': bucket, 'Key': obj['Key']}, target_bucket, Key=f"{target_key}/{suffix}")
            # s3.delete_object(Bucket=bucket, Key=obj['Key'])
        if not objects.get("IsTruncated", False):
            break
        continuation_token = objects.get("NextContinuationToken")

    logger.info(f"Refreshing partitions")
    execute_athena_query(f"MSCK REPAIR TABLE {target_table}", database=target_database)

        