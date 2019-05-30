from kubernetes import client
from yaml import safe_load_all

from util import evaluate_request, get_name


class VolumeManager:
    def __init__(self, namespace, **kwargs):
        with open("volumes.yml") as f:
            volume_yml = list(safe_load_all(f))
            self.nfs_volume_claim = volume_yml[0]
            self.nfs_service = volume_yml[1]
            self.nfs_server = volume_yml[2]
            self.client_volume = volume_yml[3]
            self.client_volume_claim = volume_yml[4]

        self.__namespace = namespace
        self.__v1_api = client.CoreV1Api()
        self.__v1_apps_api = client.AppsV1Api()

        self.__configure_volume(kwargs)

    def __configure_volume(self, config):
        base_name = config["name"]
        claim_name = base_name + "-nfs-pv-claim"
        server_name = base_name + "-nfs-server"
        volume_name = base_name + "-nfs"
        volume_claim_name = volume_name + "-claim"
        self.volume_claim_name = volume_claim_name

        self.nfs_volume_claim["metadata"]["name"] = claim_name

        self.nfs_service["metadata"]["name"] = server_name
        self.nfs_service["spec"]["selector"]["role"] = server_name

        self.nfs_server["metadata"]["name"] = server_name
        self.nfs_server["spec"]["selector"]["matchLabels"]["role"] = server_name
        self.nfs_server["spec"]["template"]["metadata"]["labels"]["role"] = server_name
        self.nfs_server["spec"]["template"]["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"] = claim_name

        self.client_volume["metadata"]["name"] = volume_name
        self.client_volume["spec"]["nfs"]["server"] = "{}.{}.svc.cluster.local".format(
            server_name, self.__namespace
        )

        self.client_volume_claim["metadata"]["name"] = volume_claim_name
        self.client_volume_claim["spec"]["volumeName"] = volume_name

    def create(self):
        evaluate_request(
            self.__v1_api.create_namespaced_persistent_volume_claim(
                namespace=self.__namespace, body=self.nfs_volume_claim, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_service(
                namespace=self.__namespace, body=self.nfs_service, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_apps_api.create_namespaced_deployment(
                namespace=self.__namespace, body=self.nfs_server, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_persistent_volume(
                body=self.client_volume, async_req=True
            ),
            allowed_statuses=[409],
        )
        evaluate_request(
            self.__v1_api.create_namespaced_persistent_volume_claim(
                namespace=self.__namespace,
                body=self.client_volume_claim,
                async_req=True,
            ),
            allowed_statuses=[409],
        )

    def delete(self):
        evaluate_request(
            self.__v1_api.delete_namespaced_persistent_volume_claim(
                namespace=self.__namespace, name=get_name(self.nfs_volume_claim), async_req=True
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_service(
                namespace=self.__namespace,
                name=get_name(self.nfs_service),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_apps_api.delete_namespaced_deployment(
                namespace=self.__namespace,
                name=get_name(self.nfs_server),
                async_req=True,
            )
        )
        evaluate_request(
            self.__v1_api.delete_persistent_volume(
                name=get_name(self.client_volume), async_req=True
            )
        )
        evaluate_request(
            self.__v1_api.delete_namespaced_persistent_volume_claim(
                namespace=self.__namespace,
                name=get_name(self.client_volume_claim),
                async_req=True,
            )
        )
