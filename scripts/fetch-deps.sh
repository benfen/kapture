#!/bin/sh

apt-get update -y
apt-get install inotify-tools python3 python3-pip redis-server redis-sentinel -y
pip3 install --upgrade pip
pip3 install prometheus_client
