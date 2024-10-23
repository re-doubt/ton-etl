#!/usr/bin/env python

import os
import sys
import time
from typing import Dict
import uuid
from loguru import logger
import boto3
import botocore



if __name__ == "__main__":
    source_database = os.environ.get("SOURCE_DATABASE")
    target_database = os.environ.get("TARGET_DATABASE")
    repartition_field = os.environ.get("REPARTITION_FIELD")
    source_table = os.environ.get("SOURCE_TABLE")
    target_table = os.environ.get("TARGET_TABLE")
    partition_date = os.environ.get("PARTITION_DATE")
    table_location = os.environ.get("TARGET_TABLE_LOCATION")
    tmp_location = os.environ.get("TMP_LOCATION")
    workgroup = os.environ.get("ATHENA_WORKGROUP")

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

    logger.info(f"Repartitioning table {source_database}.{source_table} => {target_database}.{target_table} "
                f"for date {partition_date} on field {repartition_field}")

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
                    'Columns': source_table_meta['Table']['StorageDescriptor']['Columns'],
                    'Location': table_location,
                    'InputFormat': 'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat',
                    'SerdeInfo': source_table_meta['Table']['StorageDescriptor']['SerdeInfo'],
                },
                "PartitionKeys": [
                    {
                        "Name": "block_date",
                        "Type": "string",
                    }
                ],
                "TableType": "EXTERNAL_TABLE",
            }
        )
        logger.info(response)
        target_table_meta = glue.get_table(DatabaseName=target_database, Name=target_table)
    
    tmp_table_name = f"{target_table}_increment_{partition_date}_{str(uuid.uuid4()).replace('-', '')}"
    tmp_table_location = f"{tmp_location}/{tmp_table_name}"
    FIELDS = ", ".join([col['Name'] for col in source_table_meta['Table']['StorageDescriptor']['Columns']])
    sql = f"""
    create table "{source_database}".{tmp_table_name}
    with (
        format = 'AVRO', 
        write_compression = 'SNAPPY',
        external_location = '{tmp_table_location}',
        bucketed_by = ARRAY['{source_table_meta['Table']['StorageDescriptor']['Columns'][0]['Name']}'],
        bucket_count = 1,
        partitioned_by = ARRAY['block_date']
    )
    as
    select {FIELDS},
    date_format(from_unixtime({repartition_field}), '%Y%m%d') as block_date
    from "{source_database}".{source_table}
    where adding_date = '{partition_date}'
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

        