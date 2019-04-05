#!/bin/bash

if [ $# -ne 2 ] ; then
  echo "\
Usage: dispatch-message.sh <TOPIC> <DATA>

DATA may be either a string or a file path.  Messages are delineated by newlines."
exit
fi

COMM="kubectl exec -t -i kafka-0 -c k8skafka -- /opt/kafka/bin/kafka-console-producer.sh --broker-list localhost:9093 --topic $1 2> /dev/null"

if [ -f "${2}" ] ; then
  cat $2 | $COMM
else
  echo $2 | $COMM
fi
