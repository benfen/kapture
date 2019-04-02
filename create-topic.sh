#!/bin/bash

if [ $# -lt 1 ] ; then
  echo "\
Usage: create-topic.sh <TOPIC> [<ZOOKEEPER_URL>] [<REPLICATION_FACTOR>] [<PARTITIONS>]

If ZOOKEPER_URL is not provided, the script will attempt to fetch the URL using minikube.
"
exit
fi

PARTITIONS=1
REP_FAC=3

if [ -z "$2" ] ; then
  ZOO=$(minikube service zk-svc --url | head -n 1 | sed "s/http:\/\///")
  echo $ZOO
else
  ZOO=$2
fi

if ! [ -z "$3" ] ; then
  REP_FAC=$3
fi

if ! [ -z "$4" ] ; then
  PARTITIONS=$4
fi

kubectl exec -it kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create --zookeeper $ZOO --replication-factor "$REP_FAC" --partitions "$PARTITIONS" --topic $1
