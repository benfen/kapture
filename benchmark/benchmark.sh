#!/bin/bash

# Ideally, at some point the cluster is so messed up that one of the commands fails and the script exits.
set -e

function prometheus_query() {
    kubectl exec -it prometheus-k8s-0 -n monitoring -c prometheus -- wget -O - -q "http://localhost:9090/api/v1/query?query=$1"
}

function get_metrics() {
    data=$(prometheus_query "sum(rate(bps_messages_produced%5B${1}%5D))")
    echo $data | grep -o "\"value\":\[.*\"" | awk '{split($0,a,","); print a[2]}'
}

namespace=test

rm -rf temp
mkdir temp
cd temp

git clone https://github.com/carbonrelay/prometheus-recipes.git --depth 1 .

echo "Deploying Prometheus"

# Script occasionally fails to deploy one or two things on the first pass.  Do it twice.
./prometheus-recipes.sh $namespace -npk
./prometheus-recipes.sh $namespace -npk

flags="-p"

if [ "on" == $redis ]; then
    flags="${flags}r"
fi

header="| Generators | Network Traffic (bytes/s) | Disk Writes (bytes/s) | Messages/s [1m] | Messages/s [2m] |"
if [ "$mode" != "fast" ]; then
    header="$header Messages/s [3m] |"
fi

if [ "$mode" == "slow" ]; then
    header="$header Messages/s [5m] |"
fi

echo $header > results.txt
results="benchmark/temp/results.txt"
# Go to the base of this repo
cd ../..
./kapture.sh $namespace 1 $flags

# Wait a minute for things to settle
sleep 60

if [ $mode == "slow" ]; then
    waiting_period=420
else
    waiting_period=300
fi

i=1
while [ $i -le $max_generators ] || [ $max_generators -le 0 ]; do
    sleep $waiting_period

    network_receive_bytes=$(get_metrics "sum(rate(node_network_receive_bytes_total%5B3m%5D))")
    disk_write_bytes=$(get_metrics "sum(rate(node_disk_written_bytes_total%5B3m%5D))")

    row="| $i | $network_receive_bytes | $disk_write_bytes | $(get_metrics "1m") | $(get_metrics "2m") | $(get_metrics "3m") |"

    if [ "$mode" == "slow" ]; then
        row="$row $(get_metrics \"5m\") |"
    fi

    echo $row >> $results

    i=$((i+1))
    kubectl scale Deployment data-loader -n $namespace --replicas $i 
done

# Clean up
./kapture.sh $namespace --delete
cd ./benchmark/temp
./prometheus-recipes.sh $namespace --delete
