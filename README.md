# re:doubt Indexing pipeline

The repository contains the code for the indexing pipeline of the re:doubt data warehouse. It consists of the main parts:
* [ton-indexer-worker](https://github.com/toncenter/ton-index-worker) - C++ indexer by the Toncenter team
* Postgres DB + Kafka + Debeizum
* [Parser](./parser/) - simple tool to handle new entries in the DB and parse it

# Debeizium Configuration

````sh
curl --location 'http://localhost:8083/connectors' \
   --header 'Accept: application/json' \
   --header 'Content-Type: application/json' \
   --data '{
   "name": "cdc-using-debezium-connector",
   "config": {
       "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
       "database.hostname": "postgres",
       "database.port": "5432",
       "database.user": "postgres",
       "database.password": "???????",
       "database.dbname": "ton_index_v2",
       "topic.prefix": "ton",
       "topic.creation.default.partitions": 10,
       "topic.creation.default.replication.factor": 1,
       "transforms": "unwrap",
       "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
       "transforms.unwrap.add.fields": "op,table,lsn,source.ts_ms",
       "transforms.unwrap.add.headers": "db",
       "key.converter": "org.apache.kafka.connect.json.JsonConverter",
       "key.converter.schemas.enable": "false",
       "value.converter": "org.apache.kafka.connect.json.JsonConverter",
       "value.converter.schemas.enable": "false",
       "producer.override.max.request.size": "1073741824",
   }
}'
````

Also override max size settings in Kafka server.properties:
``sh
buffer.memory=200000000
max.request.size=200000000
message.max.bytes=200000000
max.partition.fetch.bytes=200000000
``

TODO:
* indexer worker configuration
* overall architecture chart
* parser configuration
* DB schema and indecies