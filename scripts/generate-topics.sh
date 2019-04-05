#!/bin/bash
COUNTER=$1

while [ $COUNTER -gt 0 ]
do
    COUNTER=$(( $COUNTER - 1 ))
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER_URL --replication-factor 1 --partitions 3 --topic "Store_$COUNTER" --if-not-exists
done