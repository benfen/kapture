#!/bin/sh

(
    cd dummy-kafka-messenger
    gradle build
)

docker build . --tag benfen/dummy-kafka-messenger:latest

read -p "Push container to dockerhub?" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker push benfen/dummy-kafka-messenger:latest
fi
