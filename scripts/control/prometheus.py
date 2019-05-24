from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class PrometheusManager:
    def __init__(self, namespace):
        with open("prometheus.yml") as f:
            prometheus_yml = list(safe_load_all(f))
            self.redis_metrics = prometheus_yml[0]
            self.bps_metrics = prometheus_yml[1]

        self.namespace = namespace
        self.custom_objects_api = client.CustomObjectsApi()
        self.group = "monitoring.coreos.com"
        self.version = "v1"
        self.plural = "servicemonitors"

    def create(self):
        evaluate_request(
            self.custom_objects_api.create_namespaced_custom_object(
                namespace=self.namespace,
                body=self.redis_metrics,
                async_req=True,
                group=self.group,
                version=self.version,
                plural=self.plural,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.custom_objects_api.create_namespaced_custom_object(
                namespace=self.namespace,
                body=self.bps_metrics,
                async_req=True,
                group=self.group,
                version=self.version,
                plural=self.plural,
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.custom_objects_api.delete_namespaced_custom_object(
                namespace=self.namespace,
                body={},
                name=get_name(self.redis_metrics),
                async_req=True,
                group=self.group,
                version=self.version,
                plural=self.plural,
            )
        )
        evaluate_request(
            self.custom_objects_api.delete_namespaced_custom_object(
                namespace=self.namespace,
                body={},
                name=get_name(self.bps_metrics),
                async_req=True,
                group=self.group,
                version=self.version,
                plural=self.plural,
            )
        )
