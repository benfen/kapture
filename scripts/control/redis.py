from kubernetes import client
from kubernetes.stream import stream
from time import sleep
from yaml import safe_load_all

from util import evaluate_request, get_name


def exec_redis_command(name, namespace, command):
    return stream(
        client.CoreV1Api().connect_get_namespaced_pod_exec,
        name,
        namespace,
        command=command,
        stderr=False,
        stdin=False,
        stdout=True,
        tty=False,
        container="sentinel",
    )


class RedisManager:
    def __init__(self, namespace, config):
        with open("redis.yml") as f:
            redis_yml = list(safe_load_all(f))
            self.redis_master = redis_yml[0]
            self.redis_service = redis_yml[1]
            self.redis_slave_controller = redis_yml[2]
            self.redis_sentinel_controller = redis_yml[3]
            self.redis_metrics_service = redis_yml[4]
            self.redis_connector = redis_yml[5]

        self.config = config
        self.namespace = namespace
        self.v1_api = client.CoreV1Api()
        self.v1_apps_api = client.AppsV1Api()

    def __wait_for_redis_master(self):
        sentinel_started = False
        while not sentinel_started:
            sleep(2)
            try:
                out = exec_redis_command(
                    get_name(self.redis_master),
                    self.namespace,
                    command=[
                        "redis-cli",
                        "-p",
                        "26379",
                        "sentinel",
                        "master",
                        "mymaster",
                    ],
                )
            except Exception as _:
                continue

            sentinel_started = "role-reported\nmaster" in out

        master_started = False
        while not master_started:
            sleep(2)
            try:
                out = exec_redis_command(
                    get_name(self.redis_master),
                    self.namespace,
                    command=["redis-cli", "-p", "6379", "info"],
                )
            except Exception as _:
                continue

            master_started = "role:master" in out

    def __wait_for_redis_slaves(self):
        slaves_started = False
        while not slaves_started:
            sleep(2)
            try:
                out = exec_redis_command(
                    get_name(self.redis_master),
                    self.namespace,
                    command=["redis-cli", "info"],
                )
            except Exception as _:
                continue

            slaves_started = "connected_slaves:3" in out

    def create(self):
        # Check to see if this isn't meant to deploy first
        if not self.config["deploy"]:
            return

        redis_pods = self.v1_api.list_namespaced_pod(
            namespace=self.namespace, label_selector="name=redis"
        )
        if not len(redis_pods.items) == 0:
            return

        evaluate_request(
            self.v1_api.create_namespaced_pod(
                namespace=self.namespace, body=self.redis_master, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace, body=self.redis_service, async_req=True
            ),
            allowed_statuses=[409],
        )

        self.__wait_for_redis_master()

        evaluate_request(
            self.v1_api.create_namespaced_replication_controller(
                namespace=self.namespace,
                body=self.redis_slave_controller,
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.create_namespaced_replication_controller(
                namespace=self.namespace,
                body=self.redis_sentinel_controller,
                async_req=True,
            )
        )

        self.__wait_for_redis_slaves()

        self.v1_api.delete_namespaced_pod(
            namespace=self.namespace, name=get_name(self.redis_master)
        )

        evaluate_request(
            self.v1_api.create_namespaced_service(
                namespace=self.namespace,
                body=self.redis_metrics_service,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.v1_apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=self.redis_connector, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.v1_api.delete_namespaced_pod(
                namespace=self.namespace,
                name=get_name(self.redis_master),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.redis_service),
                async_req=True,
            )
        )

        evaluate_request(
            self.v1_api.delete_namespaced_replication_controller(
                namespace=self.namespace,
                name=get_name(self.redis_slave_controller),
                async_req=True,
                propagation_policy="Background",
            )
        )
        evaluate_request(
            self.v1_api.delete_namespaced_replication_controller(
                namespace=self.namespace,
                name=get_name(self.redis_sentinel_controller),
                async_req=True,
                propagation_policy="Background",
            )
        )

        evaluate_request(
            self.v1_api.delete_namespaced_service(
                namespace=self.namespace,
                name=get_name(self.redis_metrics_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.v1_apps_api.delete_namespaced_deployment(
                namespace=self.namespace,
                name=get_name(self.redis_connector),
                async_req=True,
                propagation_policy="Background",
            )
        )
