#!/bin/bash

# Ideally, at some point the cluster is so messed up that one of the commands fails and the script exits.
set -e

namespace=test

rm -rf temp
mkdir temp
cd temp

git clone https://github.com/carbonrelay/prometheus-recipes.git --depth 1 .

echo "Deploying Prometheus"

# Script occasionally fails to deploy one or two things on the first pass.  Do it twice.
./prometheus-recipes.sh $namespace --no-deploy-alertmanager --no-deploy-grafana --no-deploy-kube-state-metrics --no-deploy-node-exporter --no-deploy-prometheus-adapter
./prometheus-recipes.sh $namespace --no-deploy-alertmanager --no-deploy-grafana --no-deploy-kube-state-metrics --no-deploy-node-exporter --no-deploy-prometheus-adapter

flags="-p"

if [ "on" == $redis ]; then
    flags="${flags}r"
fi

seperator="-----------------------------------"
echo $seperator > results.txt
results="benchmark/temp/results.txt"
prometheus_url="$(minikube service -n monitoring prometheus-k8s --url)"
# Go to the base of this repo
cd ../..
./kapture.sh $namespace 1 $flags

# Wait a minute for things to settle
sleep 60

if [ $mode == "fast" ]; then
    waiting_period=180
elif [ $mode == "slow" ]; then
    waiting_period=420
else
    waiting_period=300
fi

i=1
while [ $i -le $max_generators ] || [ $max_generators -le 0 ]; do
    sleep $waiting_period

    one=$(curl "$prometheus_url/api/v1/query?query=sum(rate(bps_messages_produced%5B1m%5D))" | grep -o "\"value\":\[.*\"" | awk '{split($0,a,","); print a[2]}')
    echo "Generators : $i ; Messages/s[1m] : $one" >> $results

    two=$(curl "$prometheus_url/api/v1/query?query=sum(rate(bps_messages_produced%5B2m%5D))" | grep -o "\"value\":\[.*\"" | awk '{split($0,a,","); print a[2]}')
    echo "Generators : $i ; Messages/s[2m] : $two" >> $results

    if [ "$mode" != "fast" ]; then
        three=$(curl "$prometheus_url/api/v1/query?query=sum(rate(bps_messages_produced%5B3m%5D))" | grep -o "\"value\":\[.*\"" | awk '{split($0,a,","); print a[2]}')
        echo "Generators : $i ; Messages/s[3m] : $three" >> $results
    fi

    if [ "$mode" == "slow" ]; then
        five=$(curl "$prometheus_url/api/v1/query?query=sum(rate(bps_messages_produced%5B5m%5D))" | grep -o "\"value\":\[.*\"" | awk '{split($0,a,","); print a[2]}')
        echo "Generators : $i ; Messages/s[5m] : $five" >> $results
    fi

    echo $seperator >> $results

    i=$((i+1))
    kubectl scale Deployment data-loader -n $namespace --replicas $i 
done

# Clean up
./kapture.sh $namespace --delete
cd ./benchmark/temp
./prometheus-recipes.sh $namespace --delete
