#!/bin/bash

if [ $# -lt 1 ] ; then
  echo "\
Usage: create-topic.sh [<TOPIC>] [<PARTITIONS>] [<REPLICATION_FACTOR>]

If ZOOKEPER_URL is not provided, the script will attempt to fetch the URL using minikube."
exit
fi

PARTITIONS=3
REP_FAC=3

ZOO=$(kubectl exec kafka-0 -- printenv | grep ZK_SVC_SERVICE_HOST | cut -d "=" -f 2)
ZOO=$ZOO:$(kubectl exec kafka-0 -- printenv | grep "ZK_SVC_SERVICE_PORT=" | cut -d "=" -f 2)

if ! [ -z "$4" ] ; then
  REP_FAC=$4
fi

if ! [ -z "$3" ] ; then
  PARTITIONS=$3
fi

kubectl exec -it kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOO --replication-factor "$REP_FAC" --partitions "$PARTITIONS" --topic $1
