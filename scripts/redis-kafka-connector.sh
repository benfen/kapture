#!/bin/sh

/opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER_URL --topic db-messages --replication-factor 3 --partitions 1 --if-not-exists
/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_URL \
    --topic db-messages | awk '{split($0,a,\":\"); print \"set\", a[1], a[2]}' | redis-cli -h $REDIS_URL