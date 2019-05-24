from kubernetes import client, config
import os

from kafka import KafkaManager
from load_gen import LoadGenManager
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


def main():
    try:
        config.load_kube_config()
    except Exception as _:
        config.load_incluster_config()

    namespace = "test"
    zookeeper = ZookeeperManager(namespace)
    kafka = KafkaManager(namespace)
    redis = RedisManager(namespace)
    load_gen = LoadGenManager(namespace)

    if os.environ.get("delete") is None:
        initialize_namespace(namespace)
        zookeeper.create()
        kafka.create()
        redis.create()
        load_gen.create()
    else:
        zookeeper.delete()
        kafka.delete()
        redis.delete()
        load_gen.delete()


if __name__ == "__main__":
    main()
