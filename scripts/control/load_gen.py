from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class LoadGenManager:
    def __init__(self, namespace):
        with open("load-gen.yml") as f:
            load_gen_yml = list(safe_load_all(f))
            self.load_gen_service = load_gen_yml[0]
            self.load_gen_deployment = load_gen_yml[1]

        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_apps_api = client.AppsV1Api()

    def create(self):
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace, body=self.load_gen_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.load_gen_deployment, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.load_gen_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace,
                name=get_name(self.load_gen_deployment),
                async_req=True,
                propagation_policy="Background",
            )
        )
