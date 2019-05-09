#!/bin/bash

TAG=$1

(
    BASEDIR=$(dirname $0)
    cd $BASEDIR/..

    if [ -z $TAG ]; then
        docker build . --tag benfen/dummy-kafka-messenger:latest
    else
        docker build . --tag "benfen/dummy-kafka-messenger:$TAG"
        docker push "benfen/dummy-kafka-messenger:$TAG"
    fi
)
