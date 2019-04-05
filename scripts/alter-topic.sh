#!/bin/bash

if [ $# -lt 1 ] ; then
  echo "\
Usage: alter-topic.sh <TOPIC> [<PARTITIONS>]"
exit
fi

PARTITIONS=3

ZOO=$(kubectl exec kafka-0 -c k8skafka -- printenv | grep ZK_SVC_SERVICE_HOST | cut -d "=" -f 2)
ZOO=$ZOO:$(kubectl exec kafka-0 -c k8skafka -- printenv | grep "ZK_SVC_SERVICE_PORT=" | cut -d "=" -f 2)

if ! [ -z "$2" ] ; then
  PARTITIONS=$2
fi

kubectl exec kafka-0 -c k8skafka -- /opt/kafka/bin/kafka-topics.sh --alter --zookeeper $ZOO  --partitions "$PARTITIONS" --topic $1
