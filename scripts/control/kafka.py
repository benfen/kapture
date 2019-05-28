from kubernetes import client
from kubernetes.stream import stream
from time import sleep
from yaml import safe_load_all

from util import evaluate_request, get_name


class KafkaManager:
    def __init__(self, namespace, config):
        with open("kafka.yml") as f:
            kafka_yml = list(safe_load_all(f))
            self.kafka_service = kafka_yml[0]
            self.kafka_pdb = kafka_yml[1]
            self.kafka = kafka_yml[2]
            self.kafka_metrics_service = kafka_yml[3]
            self.kafka_metrics = kafka_yml[4]
            self.kafka_pvc = kafka_yml[5]

        self.config = config
        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_policy_api = client.PolicyV1beta1Api()
        self.v1_apps_api = client.AppsV1Api()
        self.__configure_kafka()

    def __configure_kafka(self):
        """Modifies kube config items for Kafka based on the internal configuration

        Currently, the update to kafka include:
            - Configuring Kafka to use a persistent volume claim
        """
        if self.config["usePersistentVolume"]:
            volumes = self.kafka["spec"]["template"]["spec"]["volumes"]
            empty_dir = volumes.pop(0)
            pvc = client.V1PersistentVolumeClaimVolumeSource(empty_dir["name"])
            volumes.push(pvc.to_dict())

    def create(self):
        """Create kafka items in the cluster.

        Creates all the parts of the kafka deployment in the cluster.  If items already exist in
        the cluster, those items will be quietly ignored.
        """
        if self.config["usePersistentVolume"]:
            evaluate_request(
                self.v1_api.create_namespaced_persistent_volume_claim(
                    namespace=self.namespace, body=self.kafka_pvc, async_req=True
                ),
                allowed_statuses=[409],
            )
        else:
            evaluate_request(
                self.v1_api.delete_namespaced_persistent_volume_claim(
                    namespace=self.namespace, name=get_name(self.kafka_pvc), async_req=True
                )
            )

        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace, body=self.kafka_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_policy_api.create_namespaced_pod_disruption_budget(
                namespace=self.namespace, body=self.kafka_pdb, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_stateful_set(
                namespace=self.namespace, body=self.kafka, async_req=True
            ),
            allowed_statuses=[409],
        )

        # Wait for Kafka to register itself with zookeeper before proceeding
        kafka_started = False
        while not kafka_started:
            try:
                out = stream(
                    self.v1_api.connect_get_namespaced_pod_exec,
                    "zk-0",
                    self.namespace,
                    command=[
                        "bash",
                        "-c",
                        "echo dump | nc localhost 2181 | grep brokers",
                    ],
                    stderr=False,
                    stdin=False,
                    stdout=True,
                    tty=False,
                )
                kafka_started = len(out.split()) == 3
            except Exception as _:
                sleep(2)

        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace,
                body=self.kafka_metrics_service,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.kafka_metrics, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        """Delete all Kafka artifacts within the cluster

        Removes all the Kafka artifacts within the cluster safely - if something does not already
        exist within the cluster, it will be ignored.
        """
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.kafka_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_policy_api.delete_namespaced_pod_disruption_budget(
                namespace=self.namespace, name=get_name(self.kafka_pdb), async_req=True
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_stateful_set(
                namespace=self.namespace,
                name=get_name(self.kafka),
                async_req=True,
                propagation_policy="Background",
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.kafka_metrics_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace,
                name=get_name(self.kafka_metrics),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_persistent_volume_claim(
                namespace=self.namespace, name=get_name(self.kafka_pvc), async_req=True
            )
        )
