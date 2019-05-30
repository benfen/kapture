from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class LoadGenManager:
    """Manager for load generation resources in the cluster

    Attributes:
        load_gen_service - JSON representation of the service used to access the load generators.  Since the
            load generators are primarily meant to send data out, this is not currently used.
        load_gen_deployment - JSON representation of the deployment that houses the load generators
    """

    def __init__(self, namespace, config):
        """Initializes the load generation manager with configuration from the load generation yml file

        Args:
            namespace - Namespace to deploy the load generation resources to; string
            config - Configuration options for the load generation resources; dict
        """
        with open("load-gen.yml") as f:
            load_gen_yml = list(safe_load_all(f))
            self.load_gen_service = load_gen_yml[0]
            self.load_gen_deployment = load_gen_yml[1]

        self.__config = config
        self.__namespace = namespace
        self.__v1_api = client.CoreV1Api()
        self.__v1_apps_api = client.AppsV1Api()

        self.__config_load_gen()

    def __config_load_gen(self):
        """Uses the configuration stored in this instance to modify the loaded yml
        """
        self.load_gen_deployment["spec"]["replicas"] = self.__config["bpsReplicas"]
        self.load_gen_deployment["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = self.__config["kapture_version"]

    def create(self):
        """Creates the load generation resources in the cluster
        """
        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace, body=self.load_gen_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_deployment(
                namespace=self.__namespace,
                body=self.load_gen_deployment,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        # Make a second call to patch the configuration to make sure changes in replicas are applied
        # TODO: Investigate making a utility method similar to `kubectl apply`
        evaluate_request(
            self.__v1_apps_api.patch_namespaced_deployment(
                namespace=self.__namespace,
                body=self.load_gen_deployment,
                name=get_name(self.load_gen_deployment),
                async_req=True,
            )
        )

    def delete(self):
        """Removes the load generation resources from the cluster
        """
        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.load_gen_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_deployment(
                namespace=self.__namespace,
                name=get_name(self.load_gen_deployment),
                async_req=True,
                propagation_policy="Background",
            )
        )
