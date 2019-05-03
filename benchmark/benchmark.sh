#!/bin/bash

# Ideally, at some point the cluster is so messed up that one of the commands fails and the script exits.
set -e

function prometheus_query() {
    data=$(kubectl exec prometheus-k8s-0 -n monitoring -c prometheus -- wget -O - -q "http://localhost:9090/api/v1/query?query=$1")
    echo $data | grep -o "\"value\":\[.*\"" | awk '{split($0,a,","); gsub(/"/, "", a[2]); print a[2]}'
}

function get_messages_metric() {
    prometheus_query "sum(rate(bps_messages_produced%5B${1}%5D))"
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

header="| Generators | CPU Usage (% of Cluster) | Memory Usage (% of Cluster) | Network Traffic (bytes/s) | Disk Writes (bytes/s) | Messages/s [1m] | Messages/s [2m] |"
header2="|-|-|-|-|-|-|-|"
if [ "$mode" != "fast" ]; then
    header="$header Messages/s [3m] |"
    header2="$header2-|"
fi

if [ "$mode" == "slow" ]; then
    header="$header Messages/s [5m] |"
    header2="$header2-|"
fi

echo $header > results.txt
echo $header2 >> results.txt
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

messages_declining=0
old_count=0
node_count=$(kubectl get nodes --no-headers | wc -l)
i=1
while { [ "$max_generators" -le 0 ] && [ "$messages_declining" -eq 0 ]; } ||  [ "$i" -le "$max_generators" ]; do
    sleep $waiting_period

    cpu_usage=$(kubectl top nodes --no-headers | awk -v count="$node_count" '{print $3/count}' | paste -sd+ - | bc)
    memory_usage=$(kubectl top nodes --no-headers | awk -v count="$node_count" '{print $5/count}' | paste -sd+ - | bc)
    network_receive_bytes=$(prometheus_query "sum(rate(node_network_receive_bytes_total%5B3m%5D))")
    disk_write_bytes=$(prometheus_query "sum(rate(node_disk_written_bytes_total%5B3m%5D))")

    messages_two=$(get_messages_metric "2m")
    row="| $i | $cpu_usage | $memory_usage | $network_receive_bytes | $disk_write_bytes | $(get_messages_metric "1m") | $messages_two | $(get_messages_metric "3m") |"

    if [ "$mode" == "slow" ]; then
        row="$row $(get_messages_metric \"5m\") |"
    fi

    echo $row >> $results

    if [ "$messages_declining" -eq 1 ] || [ $(echo "$old_count > $messages_two" | bc -l) -eq 1 ]; then
        messages_declining=1
    else
        old_count=$messages_two
    fi

    i=$((i+1))
    echo "Scaling load generators now to $i..."
    kubectl scale Deployment data-loader -n $namespace --replicas $i
    echo "Done scaling !"
done

if [ "$characterize" == "on" ]; then
    if ! [ -z $(command -v python3) ]; then
        python3 benchmark/characterization.py $results $redis
    elif ! [ -z $(command -v python) ]; then
        python benchmark/characterization.py $results $redis
    elif ! [ -z $(command -v py) ]; then
        py benchmark/characterization.py $results $redis
    else
        echo "Unable to locate python on this machine.  Skipping characterization..."
    fi
fi

echo "Removing created Kapture resources from the cluster..."
./kapture.sh $namespace --delete > /dev/null 2> /dev/null
cd ./benchmark/temp
echo "Removing created Prometheus resources from the cluster..."
./prometheus-recipes.sh $namespace --delete > /dev/null 2> /dev/null
echo "Cleaning up created testing namespace..."
kubectl delete namespace $namespace > /dev/null 2> /dev/null
