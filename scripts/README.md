# Scripts

All scripts meant for general use within Kapture (not for benchmarking) are located here.  Scripts located inside the `container` folder are scripts that are added to the Docker image built for this project.  Scripts located inside the `control` folder are incorporated into the container as part of the controller for Kapture.

* [`fetch-deps.sh`](container/fetch-deps.sh) - Fetches dependencies needed for the kafka/redis connection portions of the cluster to function.  Expects to be run in an Alpine container (i.e. uses `apk`).  Intended for use within one of the containers.
* [`generate-topics.sh`](container/generate-topics.sh) - Generates a list of topics based on an input variable from the user.  Topics created will be in the format: "Store_$NUMBER".  Intended for use within one of the containers.
* [`kafka-metrics.py`](container/kafka-metrics.py) - Starts up a prometheus server to grab specific Kapture metrics from Kafka.
* [`postgres-connector.py`](container/postgres-connector.py) - Starts up a postgres connector in python that connects to a postgres table, creates the bps tables if they do not exist, and then reads the standard input line by line to pass data into postgres.
* [`postgres-connector.sh`](container/postgres-connector.sh) - Starts up the Kafka connector to pass data into the python connector.
* [`redis-connector.sh`](container/redis-connector.sh) - Initializes a connector between Redis and Kafka to read messages from a Kafka spout and store them into Redis.
