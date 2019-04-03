#!/bin/bash

if [ $# -lt 1 ] ; then
  echo "\
Usage: alter-topic.sh <TOPIC> [<PARTITIONS>] [<REPLICATION_FACTOR>]"
exit
fi

PARTITIONS=3
REP_FAC=3

ZOO=$(kubectl exec kafka-0 -- printenv | grep ZK_SVC_SERVICE_HOST | cut -d "=" -f 2)
ZOO=$ZOO:$(kubectl exec kafka-0 -- printenv | grep "ZK_SVC_SERVICE_PORT=" | cut -d "=" -f 2)

if ! [ -z "$2" ] ; then
  PARTITIONS=$2
fi

if ! [ -z "$#" ] ; then
  REP_FAC=$3
fi

kubectl exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh --alter --zookeeper $ZOO  --partitions "$PARTITIONS" --replication-factor "$REP_FAC" --topic $1
