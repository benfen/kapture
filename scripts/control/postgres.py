from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class PostgresManager:
    """Manager for Postgres resources in the cluster

    Attributes:
        postgres_service - JSON representation of the service used to access Postgres
        postgres_config_map - JSON representation of the configmap used to provide configuration to
            Postgres inside the cluster.  This configmap contains items such as passwords that would
            likely be better situated in a secret; since Kapture is largely a development tool, that
            concern is largely being left unaddressed.
        postgres_pvc - JSON representation of the persistent volume claim used to back the Postgres DB
        postgres - JSON representation of the deployment that provides the Postgres DB.  There should not
            be more than 1 replica of this deployment due to the constraints of the pvc.
        postgres_connector - JSON representation of the deployment connecting Postgres to Kafka
    """

    def __init__(self, namespace, config):
        """Initializes the Postgres manager with configuration from the Postgres yml file

        Args:
            namespace - Namespace to deploy the Postgres resources to; string
            config - Configuration options for the Postgres resources; dict
        """
        with open("postgres.yml") as f:
            postgres_yml = list(safe_load_all(f))
            self.postgres_service = postgres_yml[0]
            self.postgres_config_map = postgres_yml[1]
            self.postgres_pvc = postgres_yml[2]
            self.postgres = postgres_yml[3]
            self.postgres_connector = postgres_yml[4]

        self.__config = config
        self.__namespace = namespace
        self.__v1_api = client.CoreV1Api()
        self.__v1_apps_api = client.AppsV1Api()

        self.__configure_postgres()

    def __configure_postgres(self):
        """Configure Postgres for deployment to the cluster

        The modifications to Postgres include:
            - Updating the version tag for the Kapture tag
        """
        self.postgres_connector["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = "carbonrelay/kapture:" + self.__config["kapture_version"]

    def create(self):
        """Creates the Postgres resources in the cluster
        """
        # Check to see if this isn't meant to deploy first
        if not self.__config["deploy"]:
            return
        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace, body=self.postgres_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_config_map(
                namespace=self.__namespace,
                body=self.postgres_config_map,
                async_req=True,
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_persistent_volume_claim(
                namespace=self.__namespace, body=self.postgres_pvc, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_deployment(
                namespace=self.__namespace, body=self.postgres, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_deployment(
                namespace=self.__namespace, body=self.postgres_connector, async_req=True
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        """Removes the Postgres resources from the cluster
        """
        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.postgres_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_config_map(
                namespace=self.__namespace,
                name=get_name(self.postgres_config_map),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_persistent_volume_claim(
                namespace=self.__namespace,
                name=get_name(self.postgres_pvc),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_deployment(
                namespace=self.__namespace, name=get_name(self.postgres), async_req=True
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_deployment(
                namespace=self.__namespace,
                name=get_name(self.postgres_connector),
                async_req=True,
            )
        )
