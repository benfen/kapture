#!/bin/sh

for ((i = 0; i < $1; i++))
do
  /opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER_URL --replication-factor 3 --partitions 3 --topic "Store_$1"
done