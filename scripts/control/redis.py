from kubernetes import client
from kubernetes.stream import stream
from time import sleep
from yaml import safe_load_all

from util import evaluate_request, get_name


def exec_redis_command(name, namespace, command):
    """Execute a single command on a Redis sentinel container in the cluster

    Args:
        name - Name of the pod to execute the command inside of; string
        namespace - Namespace that the pod lives in; string
        command - Command to run within the pod.  Expects an array of strings

    Returns:
        Output from the command as a string

    Raises:
        If the command passed to the container fails or if the container itself does not exist,
        then the attempt to execute the command will fail and raise an exception
    """
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
    """Manager for Redis related resources in the cluster

    Attributes:
        redis_master - JSON representation of the Redis master resource.  This is used only temporarily
            to boostrap the clustering of Redis
        redis_service - JSON representation of the service used to access Redis
        redis_slave_controller - JSON representation of the deployment resource for Redis slaves
        redis_sentinel_controller - JSON representation of the deployment resource for Redis sentinels
        redis_metrics_service - JSON representation of the service used to access Redis metrics
        redis_connector - JSON representation of the pod used to connect Kafka to Redis
    """

    def __init__(self, namespace, config):
        """Initializes the Redis manager with configuration from the Redis yml file

        Args:
            namespace - Namespace to deploy the Redis resources to; string
            config - Configuration options for the Redis resources; dict
        """
        with open("redis.yml") as f:
            redis_yml = list(safe_load_all(f))
            self.redis_master = redis_yml[0]
            self.redis_service = redis_yml[1]
            self.redis_slave_controller = redis_yml[2]
            self.redis_sentinel_controller = redis_yml[3]
            self.redis_metrics_service = redis_yml[4]
            self.redis_connector = redis_yml[5]

        self.__config = config
        self.__namespace = namespace
        self.__v1_api = client.CoreV1Api()
        self.__v1_apps_api = client.AppsV1Api()

        self.__configure_redis()

    def __configure_redis(self):
        """Configures the Redis for the cluster

        The modifications to Redis include:
            - Updating the version tag for the Kapture container
        """
        self.redis_connector["spec"]["template"]["spec"]["containers"][0]["image"] = (
            "carbonrelay/kapture:" + self.__config["kapture_version"]
        )

    def __wait_for_redis_master(self):
        """Waits for the Redis master to startup

        Connects to the Redis master pod and waits until it sees that the slaves are connected.
        Ideally, this should ensure that when the Redis slaves startup they are able to talk
        to the Redis master immediately and connect
        """
        sentinel_started = False
        while not sentinel_started:
            sleep(2)
            try:
                out = exec_redis_command(
                    get_name(self.redis_master),
                    self.__namespace,
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
                    self.__namespace,
                    command=["redis-cli", "-p", "6379", "info"],
                )
            except Exception as _:
                continue

            master_started = "role:master" in out

    def __wait_for_redis_slaves(self):
        """Waits for the Redis slaves to register themselves against the master
        """
        slaves_started = False
        while not slaves_started:
            sleep(2)
            try:
                out = exec_redis_command(
                    get_name(self.redis_master),
                    self.__namespace,
                    command=["redis-cli", "info"],
                )
            except Exception as _:
                continue

            slaves_started = "connected_slaves:3" in out

    def create(self):
        """Create the Redis resources in the cluster
        """
        # Check to see if this isn't meant to deploy first
        if not self.__config["deploy"]:
            return

        redis_pods = self.__v1_api.list_namespaced_pod(
            namespace=self.__namespace, label_selector="name=redis"
        )
        if not len(redis_pods.items) == 0:
            return

        evaluate_request(
            self.__v1_api.create_namespaced_pod(
                namespace=self.__namespace, body=self.redis_master, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace, body=self.redis_service, async_req=True
            ),
            allowed_statuses=[409],
        )

        self.__wait_for_redis_master()

        evaluate_request(
            self.__v1_api.create_namespaced_replication_controller(
                namespace=self.__namespace,
                body=self.redis_slave_controller,
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.create_namespaced_replication_controller(
                namespace=self.__namespace,
                body=self.redis_sentinel_controller,
                async_req=True,
            )
        )

        self.__wait_for_redis_slaves()

        self.__v1_api.delete_namespaced_pod(
            namespace=self.__namespace, name=get_name(self.redis_master)
        )

        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace,
                body=self.redis_metrics_service,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_deployment(
                namespace=self.__namespace, body=self.redis_connector, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        """Remove the Redis resources from the cluster
        """
        evaluate_request(
            self.__v1_api.delete_namespaced_pod(
                namespace=self.__namespace,
                name=get_name(self.redis_master),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.redis_service),
                async_req=True,
            )
        )

        evaluate_request(
            self.__v1_api.delete_namespaced_replication_controller(
                namespace=self.__namespace,
                name=get_name(self.redis_slave_controller),
                async_req=True,
                propagation_policy="Background",
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_replication_controller(
                namespace=self.__namespace,
                name=get_name(self.redis_sentinel_controller),
                async_req=True,
                propagation_policy="Background",
            )
        )

        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.redis_metrics_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_deployment(
                namespace=self.__namespace,
                name=get_name(self.redis_connector),
                async_req=True,
                propagation_policy="Background",
            )
        )
