from kubernetes import client, config
import os
from yaml import safe_load

from elasticsearch import ElasticsearchManager
from kafka import KafkaManager
from load_gen import LoadGenManager
from postgres import PostgresManager
from prometheus import PrometheusManager
from redis import RedisManager
from zk import ZookeeperManager
from util import evaluate_request


def initialize_namespace(namespace, store_count=250, customers=5000, simulation=2500):
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
    return safe_load(os.environ["kapture_config"])


def main():
    try:
        config.load_kube_config()
    except Exception as _:
        config.load_incluster_config()

    kapture_config = load_config()
    namespace = kapture_config["namespace"]
    zookeeper = ZookeeperManager(namespace)
    kafka = KafkaManager(namespace, kapture_config["kafka"])
    redis = RedisManager(namespace)
    elasticsearch = ElasticsearchManager(namespace)
    postgres = PostgresManager(namespace)
    prometheus = PrometheusManager(namespace)
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
