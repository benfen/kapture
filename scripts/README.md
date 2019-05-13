# Scripts

* [`fetch-deps.sh`](./fetch-deps.sh) - Fetches dependencies needed for the kafka/redis connection portions of the cluster to function.  Expects to be run in an Alpine container (i.e. uses `apk`).  Intended for use within one of the containers.
* [`generate-topics.sh`](./generate-topics.sh) - Generates a list of topics based on an input variable from the user.  Topics created will be in the format: "Store_$NUMBER".  Intended for use within one of the containers.
* [`kafka-metrics.py`](./kafka-metrics.py) - Starts up a prometheus server to grab specific Kapture metrics from Kafka.
* [`kapture-template.m4`](./kapture-template.m4) - Template to generate the [`kapture.sh`](../kapture.sh) script at the top level.  Requires [`argbash`](https://argbash.io/) to build the actual script from the template.
* [`kapture.sh`](./kapture.sh) - The meat and potatoes of Kapture.  Creates and tears down the cluster.  See [`kapture-template.m4`](./kapture-template.m4) for a list of the environment variables that will be available to use within the script.
* [`redis-connector.sh`](./redis-connector.sh) - Initializes a connector between Redis and Kafka to read messages from a Kafka spout and store them into Redis.
