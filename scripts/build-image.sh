#!/bin/bash

TAG=$1

(
    BASEDIR=$(dirname $0)
    cd "$BASEDIR/../dummy-kafka-messenger/"
    gradle build

    cd ..
    if [ -z $TAG ]; then
        docker build . --tag benfen/dummy-kafka-messenger:latest
        exit 0
    fi

    docker build . --tag "benfen/dummy-kafka-messenger:$TAG"
    docker push "benfen/dummy-kafka-messenger:$TAG"
)
