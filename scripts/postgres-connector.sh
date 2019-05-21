#!/bin/bash

./kafka/bin/kafka-console-consumer.sh --bootstrap-server $BROKERS --topic bps-data | python3 postgres-connector.py