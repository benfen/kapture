from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class LogstashManager:
    """Manager for Logstash resources in the cluster

    Attributes:
        logstash_conf - JSON representation of the configmap used to create the logstash.conf file,
            primarily to establish the connection to Kafka
        logstash_yml - JSON representation of the configmap used to create the logstash.yml file and
            configure the Logstash instance
        logstash_service - JSON representation of the service used to access Logstash
        logstash - JSON representation of the StatefulSet that runs Logstash
    """

    def __init__(self, namespace):
        """Initializes the Logstash manager with configuration from the Logstash yml file

        Args:
            namespace - Namespace to deploy the Logstash resources to; string
        """
        with open("logstash.yml") as f:
            logstash_yml = list(safe_load_all(f))
            self.logstash_conf = logstash_yml[0]
            self.logstash_yml = logstash_yml[1]
            self.logstash_service = logstash_yml[2]
            self.logstash = logstash_yml[3]

        self.__namespace = namespace
        self.__v1_api = client.CoreV1Api()
        self.__v1_apps_api = client.AppsV1Api()

    def create(self):
        """Creates the Logstash resources in the cluster
        """
        evaluate_request(
            self.__v1_api.create_namespaced_config_map(
                namespace=self.__namespace, body=self.logstash_conf, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_config_map(
                namespace=self.__namespace, body=self.logstash_yml, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace, body=self.logstash_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_stateful_set(
                namespace=self.__namespace, body=self.logstash, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        """Removes the Logstash resources from the cluster
        """
        evaluate_request(
            self.__v1_api.delete_namespaced_config_map(
                namespace=self.__namespace,
                name=get_name(self.logstash_conf),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_config_map(
                namespace=self.__namespace,
                name=get_name(self.logstash_yml),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.logstash_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_stateful_set(
                namespace=self.__namespace,
                name=get_name(self.logstash),
                async_req=True,
                propagation_policy="Background",
            )
        )
