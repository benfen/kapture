#!/bin/sh

apk add --upgrade redis
wget -P /opt http://apache.claz.org/kafka/2.2.0/kafka_2.12-2.2.0.tgz
mkdir -p /opt/kafka
tar -zxvf /opt/kafka_2.12-2.2.0.tgz -C /opt/kafka --strip-components=1