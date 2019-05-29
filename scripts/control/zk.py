from kubernetes import client
from kubernetes.stream import stream
from time import sleep
from yaml import safe_load_all

from util import evaluate_request, get_name


class ZookeeperManager:
    """Manager for Zookeeper related resources in the cluster

    Manages creation, deletion, and modification of Zookepeer resources in the Kubernetes cluster.

    Attributes:
        zk_service - JSON representation of the Zookeeper service resource used to access Zookeeper
        zk_configmap - JSON representation of the configmap used to provide configuration options
        zk_pdb - JSON representation of the pod disruption budget for the zookeeper instances
        zk - JSON representation of the deployment for running Zookeeper
    """

    def __init__(self, namespace):
        """Initializes the Zookeeper manager with configuration from the Zookeeper yml file

        Args:
            namespace - Namespace to deploy the Zookeeper resources to; string
        """
        with open("zk.yml") as f:
            zk_yml = list(safe_load_all(f))
            self.zk_service = zk_yml[0]
            self.zk_configmap = zk_yml[1]
            self.zk_pdb = zk_yml[2]
            self.zk = zk_yml[3]

        self.__namespace = namespace
        self.__v1_api = client.CoreV1Api()
        self.__v1_policy_api = client.PolicyV1beta1Api()
        self.__v1_apps_api = client.AppsV1Api()

    def create(self):
        """Create all Zookeeper items in the cluster

        Starts up the Zookeeper resources and then attempts to wait for Zookeeper to be ready
        for brokers to register before returning.  The waiting period currently seems to be a little
        too short.
        """
        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace, body=self.zk_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_config_map(
                namespace=self.__namespace, body=self.zk_configmap, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_policy_api.create_namespaced_pod_disruption_budget(
                namespace=self.__namespace, body=self.zk_pdb, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_stateful_set(
                namespace=self.__namespace, body=self.zk, async_req=True
            ),
            allowed_statuses=[409],
        )

        zk_started = False
        while not zk_started:
            try:
                stream(
                    self.__v1_api.connect_get_namespaced_pod_exec,
                    "zk-0",
                    self.__namespace,
                    command=["zkOk.sh"],
                    stderr=False,
                    stdin=False,
                    stdout=True,
                    tty=False,
                )
                zk_started = True
            except Exception as _:
                sleep(2)

    def delete(self):
        """Removes all Zookeeper resources from the cluster
        """
        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.zk_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_config_map(
                namespace=self.__namespace,
                name=get_name(self.zk_configmap),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_policy_api.delete_namespaced_pod_disruption_budget(
                namespace=self.__namespace, name=get_name(self.zk_pdb), async_req=True
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_stateful_set(
                namespace=self.__namespace,
                name=get_name(self.zk),
                async_req=True,
                propagation_policy="Background",
            )
        )
