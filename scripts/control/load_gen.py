from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class LoadGenManager:
    def __init__(self, namespace, config):
        with open("load-gen.yml") as f:
            load_gen_yml = list(safe_load_all(f))
            self.load_gen_service = load_gen_yml[0]
            self.load_gen_deployment = load_gen_yml[1]

        self.config = config
        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_apps_api = client.AppsV1Api()
        self.__config_load_gen()

    def __config_load_gen(self):
        self.load_gen_deployment["spec"]["replicas"] = self.config.bpsReplicas

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
        # Make a second call to patch the configuration to make sure changes in replicas are applied
        # TODO: Investigate making a utility method similar to `kubectl apply`
        evaluate_request(
            self.v1_apps_api.patch_namespaced_deployment(
                namespace=self.namespace,
                body=self.load_gen_deployment,
                name=get_name(self.load_gen_deployment),
                async_req=True,
            )
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
