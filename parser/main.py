#!/usr/bin/env python
import psycopg2
import os
import time
import json
import traceback
from loguru import logger
from db import DB
from kafka import KafkaConsumer
from parsers import generate_parsers


if __name__ == "__main__":
    group_id = os.environ.get("KAFKA_GROUP_ID")
    topics = os.environ.get("KAFKA_TOPICS", "ton.public.latest_account_states,ton.public.messages,ton.public.nft_transfers")
    log_interval = int(os.environ.get("LOG_INTERVAL", '10'))
    supported_parsers = os.environ.get("SUPPORTED_PARSERS", "*")
    db = DB()

    consumer = KafkaConsumer(
            group_id=group_id,
            bootstrap_servers=os.environ.get("KAFKA_BROKER"),
            auto_offset_reset='earliest'
            )
    for topic in topics.split(","):
        logger.info(f"Subscribing to {topic}")
        consumer.subscribe(topic)
    # TODO add prometheus metrics here

    last = time.time()
    total = 0
    successful = 0
    PARSERS = generate_parsers(None if supported_parsers == '*' else set(supported_parsers.split(",")))
    for msg in consumer:
        # logger.info(msg)
        try:
            total += 1
            handled = 0
            obj = json.loads(msg.value.decode("utf-8"))
            __op = obj.get('__op', None)
            if __op == 'd': # ignore deletes
                continue
            for parser in PARSERS.get(msg.topic, []):
                if parser.handle(obj, db):
                    handled = 1
            successful += handled
            now = time.time()
            if now - last > log_interval:
                logger.info(f"{1.0 * total / (now - last):0.2f} Kafka messages per second, {100.0 * successful / total:0.2f}% handled")
                last = now
                successful = 0
                total = 0
        except Exception as e:
            logger.error(f"Failted to process item {msg}: {e} {traceback.format_exc()}")
            raise
