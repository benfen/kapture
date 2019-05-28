from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class PostgresManager:
    def __init__(self, namespace, config):
        with open("postgres.yml") as f:
            postgres_yml = list(safe_load_all(f))
            self.postgres_service = postgres_yml[0]
            self.postgres_config_map = postgres_yml[1]
            self.postgres_pvc = postgres_yml[2]
            self.postgres = postgres_yml[3]
            self.postgres_connector = postgres_yml[4]

        self.config = config
        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_apps_api = client.AppsV1Api()

    def create(self):
        # Check to see if this isn't meant to deploy first
        if not self.config["deploy"]:
            return
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace, body=self.postgres_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_config_map(
                namespace=self.namespace, body=self.postgres_config_map, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_persistent_volume_claim(
                namespace=self.namespace, body=self.postgres_pvc, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.postgres, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.postgres_connector, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.postgres_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_config_map(
                namespace=self.namespace,
                name=get_name(self.postgres_config_map),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_persistent_volume_claim(
                namespace=self.namespace,
                name=get_name(self.postgres_pvc),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace, name=get_name(self.postgres), async_req=True
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace,
                name=get_name(self.postgres_connector),
                async_req=True,
            )
        )
