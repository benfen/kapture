#!/bin/bash
COUNTER=$1

# Wait for all three of the initial kafka brokers to start up before proceeding to make sure that replication doesn't get messed up.
BROKERS=$(awk -F "," "{print NF-1}" <<< $(/opt/kafka/bin/zookeeper-shell.sh $ZOOKEEPER_URL <<< "ls /brokers/ids" | tail -1))

while [ $BROKERS -ne 2 ]
do
    sleep 2
    BROKERS=$(awk -F "," "{print NF-1}" <<< $(/opt/kafka/bin/zookeeper-shell.sh $ZOOKEEPER_URL <<< "ls /brokers/ids" | tail -1))
done

while [ $COUNTER -gt 0 ]
do
    COUNTER=$(( $COUNTER - 1 ))
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER_URL --replication-factor 3 --partitions 3 --topic "Store_$COUNTER" --if-not-exists
done