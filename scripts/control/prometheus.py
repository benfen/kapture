from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class PrometheusManager:
    """Manager for Prometheus resources in the cluster

    The resources in this class depend upon the ServiceMonitor CRD being defined in the cluster.
    If that CRD is not present, this manager will not function properly.

    Attributes:
        redis_metrics - JSON representation of the service monitor for metrics from Redis
        bps_metrics - JSON representation of the service monitor for metrics from the BPS load generator
    """

    def __init__(self, namespace, config):
        """Initializes the Prometheus manager with configuration from the Prometheus yml file

        Args:
            namespace - Namespace to deploy the Prometheus resources to; string
            config - Configuration options for the Prometheus resources; dict
        """
        with open("prometheus.yml") as f:
            prometheus_yml = list(safe_load_all(f))
            self.redis_metrics = prometheus_yml[0]
            self.bps_metrics = prometheus_yml[1]

        self.__config = config
        self.__namespace = namespace
        self.__custom_objects_api = client.CustomObjectsApi()
        self.__group = "monitoring.coreos.com"
        self.__version = "v1"
        self.__plural = "servicemonitors"

    def create(self):
        # Check to see if this isn't meant to deploy first
        if not self.__config["deploy"]:
            return
        evaluate_request(
            self.__custom_objects_api.create_namespaced_custom_object(
                namespace=self.__namespace,
                body=self.redis_metrics,
                async_req=True,
                group=self.__group,
                version=self.__version,
                plural=self.__plural,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__custom_objects_api.create_namespaced_custom_object(
                namespace=self.__namespace,
                body=self.bps_metrics,
                async_req=True,
                group=self.__group,
                version=self.__version,
                plural=self.__plural,
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.__custom_objects_api.delete_namespaced_custom_object(
                namespace=self.__namespace,
                body={},
                name=get_name(self.redis_metrics),
                async_req=True,
                group=self.__group,
                version=self.__version,
                plural=self.__plural,
            )
        )
        evaluate_request(
            self.__custom_objects_api.delete_namespaced_custom_object(
                namespace=self.__namespace,
                body={},
                name=get_name(self.bps_metrics),
                async_req=True,
                group=self.__group,
                version=self.__version,
                plural=self.__plural,
            )
        )
