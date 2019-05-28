from kubernetes import client
from yaml import safe_load_all

from logstash import LogstashManager
from util import evaluate_request, get_name


class ElasticsearchManager:
    def __init__(self, namespace, config):
        with open("elasticsearch.yml") as f:
            elasticsearch_yml = list(safe_load_all(f))
            self.elasticsearch_config_map = elasticsearch_yml[0]
            self.elasticsearch_master = elasticsearch_yml[1]
            self.elasticsearch_discovery = elasticsearch_yml[2]
            self.elasticsearch_data = elasticsearch_yml[3]
            self.elasticsearch_data_service = elasticsearch_yml[4]
            self.elasticsearch_client = elasticsearch_yml[5]
            self.elasticsearch_client_service = elasticsearch_yml[6]

        self.config = config
        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_apps_api = client.AppsV1Api()
        self.logstash_manager = LogstashManager(namespace)

    def create(self):
        # Check to see if this isn't meant to deploy first
        if not self.config["deploy"]:
            return
        evaluate_request(
            self.v1_api.create_namespaced_config_map(
                namespace=self.namespace,
                body=self.elasticsearch_config_map,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.elasticsearch_master, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace,
                body=self.elasticsearch_discovery,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_stateful_set(
                namespace=self.namespace, body=self.elasticsearch_data, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace,
                body=self.elasticsearch_data_service,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.elasticsearch_client, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace,
                body=self.elasticsearch_client_service,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        self.logstash_manager.create()

    def delete(self):
        evaluate_request(
            self.v1_api.delete_namespaced_config_map(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_config_map),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_master),
                async_req=True,
                propagation_policy="Background",
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_discovery),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_stateful_set(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_data),
                async_req=True,
                propagation_policy="Background",
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_data_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_client),
                async_req=True,
                propagation_policy="Background",
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.elasticsearch_client_service),
                async_req=True,
            )
        )
        self.logstash_manager.delete()
