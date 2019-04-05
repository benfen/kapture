#!/bin/bash
COUNTER=$1
echo $1

while [ $COUNTER -gt 0 ]
do
    COUNTER=$(( $COUNTER - 1 ))
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER_URL --replication-factor 3 --partitions 3 --topic "Store_$COUNTER"
done