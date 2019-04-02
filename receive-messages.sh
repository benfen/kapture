#!/bin/bash

if [ $# -lt 1 ] ; then
  echo "\
Usage: receive-messages.sh <TOPIC> [FLAGS]

FLAGS will be passed directly to the kafka script"
exit
fi

ARGS="$*"

kubectl exec -it kafka-2 -- /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9093 --topic $ARGS
