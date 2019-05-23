from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class KafkaManager:
    def __init__(self, namespace):
        with open("kafka.yml") as f:
            kafka_yml = list(safe_load_all(f))
            self.kafka_service = kafka_yml[0]
            self.kafka_pdb = kafka_yml[1]
            self.kafka = kafka_yml[2]

        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_policy_api = client.PolicyV1beta1Api()
        self.v1_apps_api = client.AppsV1beta1Api()

    def create(self):
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

    def delete(self):
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
