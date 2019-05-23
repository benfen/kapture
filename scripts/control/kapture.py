from kubernetes import config

from zk import ZookeeperManager
from kafka import KafkaManager


def main():
    try:
        config.load_kube_config()
    except Exception as _:
        config.load_incluster_config()

    zookeeper = ZookeeperManager("test")
    kafka = KafkaManager("test")
    zookeeper.delete()
    kafka.delete()


if __name__ == "__main__":
    main()
