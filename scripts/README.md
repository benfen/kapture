# Scripts

All scripts meant for general use within Kapture (not for benchmarking) are located here.  Scripts located inside the `container` folder are scripts that are added to the Docker image built for this project.

* [`fetch-deps.sh`](container/fetch-deps.sh) - Fetches dependencies needed for the kafka/redis connection portions of the cluster to function.  Expects to be run in an Alpine container (i.e. uses `apk`).  Intended for use within one of the containers.
* [`generate-topics.sh`](container/generate-topics.sh) - Generates a list of topics based on an input variable from the user.  Topics created will be in the format: "Store_$NUMBER".  Intended for use within one of the containers.
* [`kafka-metrics.py`](container/kafka-metrics.py) - Starts up a prometheus server to grab specific Kapture metrics from Kafka.
* [`postgres-connector.py`](container/postgres-connector.py) - Starts up a postgres connector in python that connects to a postgres table, creates the bps tables if they do not exist, and then reads the standard input line by line to pass data into postgres.
* [`postgres-connector.sh`](container/postgres-connector.sh) - Starts up the Kafka connector to pass data into the python connector.
* [`kapture-template.m4`](./kapture-template.m4) - Template to generate the [`kapture.sh`](../kapture.sh) script at the top level.  Requires [`argbash`](https://argbash.io/) to build the actual script from the template.
* [`kapture.sh`](./kapture.sh) - The meat and potatoes of Kapture.  Creates and tears down the cluster.  See [`kapture-template.m4`](./kapture-template.m4) for a list of the environment variables that will be available to use within the script.
* [`redis-connector.sh`](container/redis-connector.sh) - Initializes a connector between Redis and Kafka to read messages from a Kafka spout and store them into Redis.
