# Datalake exporters

Datalake exporters are responsible for exporting data from Kafka to S3. It converts messages to Avro format, 
apply additional transformations and uploads them to S3.

## Messages exporter

[AVRO schema](./schemas/messages.avsc)
Message body is stored separately in message_contents table and is not accessible immidiately during 
Kafka message handling. So we are fetching message_content from DB and also extracting 
text comment if message has it.
