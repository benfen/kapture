#!/bin/sh

function get_host() {
    redis-cli -p 26379 -h $SENTINEL_HOST INFO | grep "address=.*:6379" | grep -o "[0-9]\+.[0-9]\+.[0-9]\+.[0-9]\+"
}

while :
do
    host="$(get_host)"
    echo "Fetched Redis host: $host"
    /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $BROKERS --topic bps-data | \
        awk '{ split($0, a, "dateTime\":"); split(a[2], b, ",\"") ; gsub("\"", "\\\"", $0) ; printf "set %s \"%s\"\n",b[1],$0 }' | \
        redis-cli -x -h $host &
    PID=$!

    sleep 15
    new_host="$(get_host)"

    while [ "$host" == "$new_host" ]; do
        echo "Comparing hosts:   $host   $new_host"
        sleep 15
        new_host="$(get_host)"
    done

    echo "Detected change in Redis master.  Restarting connector..."
    kill $PID
done
