from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class LogstashManager:
    def __init__(self, namespace):
        with open("logstash.yml") as f:
            logstash_yml = list(safe_load_all(f))
            self.logstash_conf = logstash_yml[0]
            self.logstash_yml = logstash_yml[1]
            self.logstash_service = logstash_yml[2]
            self.logstash = logstash_yml[3]

        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_apps_api = client.AppsV1Api()

    def create(self):
        evaluate_request(
            self.v1_api.create_namespaced_config_map(
                namespace=self.namespace, body=self.logstash_conf, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_config_map(
                namespace=self.namespace, body=self.logstash_yml, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace, body=self.logstash_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_stateful_set(
                namespace=self.namespace, body=self.logstash, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.v1_api.delete_namespaced_config_map(
                namespace=self.namespace,
                name=get_name(self.logstash_conf),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_config_map(
                namespace=self.namespace,
                name=get_name(self.logstash_yml),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.logstash_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_stateful_set(
                namespace=self.namespace,
                name=get_name(self.logstash),
                async_req=True,
                propagation_policy="Background",
            )
        )
