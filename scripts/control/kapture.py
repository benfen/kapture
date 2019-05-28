import json
from kubernetes import client, config
import os

from elasticsearch import ElasticsearchManager
from kafka import KafkaManager
from load_gen import LoadGenManager
from postgres import PostgresManager
from prometheus import PrometheusManager
from redis import RedisManager
from zk import ZookeeperManager
from util import evaluate_request


def initialize_namespace(namespace, store_count=250, customers=5000, simulation=2500):
    """Initialize namespace and config map for kapture

    Sets up the namespace and config map for Kapture to use.  If they already exist, this method
    will quietly do nothing.
    """
    api = client.CoreV1Api()
    evaluate_request(
        api.create_namespace(
            {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": namespace}},
            async_req=True,
        ),
        allowed_statuses=[409],
    )

    evaluate_request(
        api.create_namespaced_config_map(
            namespace=namespace,
            body={
                "apiVersion": "v1",
                "data": {
                    "STORE_COUNT": str(store_count),
                    "CUSTOMERS": str(customers),
                    "SIMULATION": str(simulation),
                    "BPS_TOPIC": "bps-data",
                },
                "kind": "ConfigMap",
                "metadata": {"name": "kapture-config", "namespace": namespace},
            },
            async_req=True,
        ),
        allowed_statuses=[409],
    )


def load_config():
    """Load kapture configuration
    """
    return json.loads(os.environ["kapture_config"])


def main():
    # Update the directory to make sure filepaths to the yml files are correct
    os.chdir(os.path.dirname(__file__))

    # Attempt to load configuration from normal location and then from the cluster location
    # This is done to allow this script to be run locally for testing as well
    try:
        config.load_kube_config()
    except Exception as _:
        config.load_incluster_config()

    kapture_config = load_config()
    namespace = kapture_config["namespace"]
    zookeeper = ZookeeperManager(namespace)
    kafka = KafkaManager(namespace, kapture_config["kafka"])
    redis = RedisManager(namespace, kapture_config["redis"])
    elasticsearch = ElasticsearchManager(namespace, kapture_config["elasticsearch"])
    postgres = PostgresManager(namespace, kapture_config["postgres"])
    prometheus = PrometheusManager(namespace, kapture_config["prometheus"])
    load_gen = LoadGenManager(namespace, kapture_config["loadGen"])

    if kapture_config["action"] == "create":
        initialize_namespace(namespace)
        zookeeper.create()
        kafka.create()
        redis.create()
        elasticsearch.create()
        postgres.create()
        prometheus.create()
        load_gen.create()
    elif kapture_config["action"] == "delete":
        load_gen.delete()
        prometheus.delete()
        postgres.delete()
        elasticsearch.delete()
        redis.delete()
        kafka.delete()
        zookeeper.delete()


if __name__ == "__main__":
    main()
