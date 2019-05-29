#!/bin/sh

inotifywait -mq -e create --format "%w%f" /data |
    while read file; do
        cat $file | /opt/kafka/bin/kafka-console-producer.sh --broker-list $BROKERS --topic bps-data
        rm $file
    done