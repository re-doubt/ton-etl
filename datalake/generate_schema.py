#!/usr/bin/env python
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
import json
import traceback
from loguru import logger
from kafka import KafkaConsumer


if __name__ == "__main__":
    schema_name = os.environ.get("DB_SCHEMA", "public")
    table_name = os.environ.get("DB_TABLE", "messages")
    ignore_fields = os.environ.get("IGNORE_FIELDS", "").split(",")

    logger.info(f"Discovering schema for {schema_name}.{table_name}")
    schema = {
        'namespace': 'ton',
        'type': 'record',
        'name': table_name,
        'fields': []
    }

    with psycopg2.connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"select * from information_schema.columns where table_schema = %s and table_name = %s", (schema_name, table_name))
            for row in cursor.fetchall():
                if row['column_name'] in ignore_fields:
                    continue
                # logger.info(f"Discovered column: {row}")
                data_type = row['data_type']
                if data_type == 'character varying' or data_type == 'character' or data_type == 'text':
                    avro_type = 'string'
                elif data_type == 'bigint':
                    avro_type = 'long'
                elif data_type == 'integer' or data_type == 'smallint':
                    avro_type = 'int'
                elif data_type == 'boolean':
                    avro_type = 'boolean'
                elif data_type == 'numeric':
                    avro_type = 'double'
                elif data_type == 'USER-DEFINED':
                    logger.warning(f"Using string for field {row['column_name']} with user-defined type")
                    avro_type = 'string'
                else:
                    raise Exception(f"Type is not supported: {data_type} for field {row['column_name']}: {row}")
                # logger.info(row)
                field = {
                    'name': row['column_name'],
                    'type': [avro_type, 'null'] if row['is_nullable'] == 'YES' else avro_type
                }
                schema['fields'].append(field)
    # adding special field from postgres
    schema['fields'].append({
        'name': '__lsn',
        'type': ['long']
    })
    schema['fields'].append({
        'name': '__id',
        'type': ['string']
    })

    with open(sys.argv[1], "wt") as out:
        out.write(json.dumps(schema, indent=2))
