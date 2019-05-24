from kubernetes import client
from kubernetes.stream import stream
from time import sleep
from yaml import safe_load_all

from util import evaluate_request, get_name


class ZookeeperManager:
    def __init__(self, namespace):
        with open("zk.yml") as f:
            zk_yml = list(safe_load_all(f))
            self.zk_service = zk_yml[0]
            self.zk_configmap = zk_yml[1]
            self.zk_pdb = zk_yml[2]
            self.zk = zk_yml[3]

        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_policy_api = client.PolicyV1beta1Api()
        self.v1_apps_api = client.AppsV1Api()

    def create(self):
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace, body=self.zk_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_config_map(
                namespace=self.namespace, body=self.zk_configmap, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_policy_api.create_namespaced_pod_disruption_budget(
                namespace=self.namespace, body=self.zk_pdb, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_stateful_set(
                namespace=self.namespace, body=self.zk, async_req=True
            ),
            allowed_statuses=[409],
        )

        zk_started = False
        while not zk_started:
            try:
                stream(
                    self.v1_api.connect_get_namespaced_pod_exec,
                    "zk-0",
                    self.namespace,
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
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace, name=get_name(self.zk_service), async_req=True
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_config_map(
                namespace=self.namespace,
                name=get_name(self.zk_configmap),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_policy_api.delete_namespaced_pod_disruption_budget(
                namespace=self.namespace, name=get_name(self.zk_pdb), async_req=True
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_stateful_set(
                namespace=self.namespace,
                name=get_name(self.zk),
                async_req=True,
                propagation_policy="Background",
            )
        )
