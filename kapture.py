from argparse import ArgumentParser
import json
import os
import subprocess


def load_kapture_version():
    """Load the version of the Kapture container

    Searches through the kustomization.yml file in this directory for the version tag stored inside and retrieves that.
    It's kind of a hack, but it keeps it down to one place to change the version for the Kapture containers.

    Returns:
        Version tag for Kapture as a string
    """
    with open("kustomization.yml") as k:
        return k.read().split("newTag:")[1].split('"')[1]


def main():
    parser = ArgumentParser()
    parser.add_argument("namespace", help="The namespace to deploy Kapture to")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete all kubernetes resources generated by Kapture (except the namespace)",
    )
    parser.add_argument(
        "generators",
        type=int,
        default=0,
        nargs="?",
        help="The maximum number of generators to run as part of this test.  "
        + "If the number is less than 1, it will run until it observes a decrease in the message throughput in Kafka",
    )
    parser.add_argument(
        "--control-locally",
        action="store_true",
        help="Flag to indiciate whether the controller should be deployed within the cluster or run locally.  If the "
        + "flag is passed, then the python controller will be run locally",
    )
    parser.add_argument(
        "-e",
        "--deploy-elasticsearch",
        action="store_true",
        help="Deploy elasticsearch and logstash as part of Kapture",
    )
    parser.add_argument(
        "--kafka-persistent-volume",
        action="store_true",
        help="Use the default persistent volume to store the Kafka topics",
    )
    parser.add_argument(
        "-r",
        "--deploy-redis",
        action="store_true",
        help="Deploy redis as part of Kapture",
    )
    parser.add_argument(
        "--redis-count",
        type=int,
        default=3,
        nargs="?",
        help="Number of redis slaves to deploy.  If redis is not deployed, this option is ignored",
    )
    parser.add_argument(
        "-o",
        "--deploy-postgres",
        action="store_true",
        help="Deploy postgres as part of Kapture",
    )
    parser.add_argument(
        "-p",
        "--deploy-prometheus",
        action="store_true",
        help="Deploy postgres as part of Kapture",
    )
    args = parser.parse_args()

    if args.delete:
        action = "delete"
    else:
        action = "create"
    kapture_version = load_kapture_version()
    config = {
        "action": action,
        "namespace": args.namespace,
        "elasticsearch": {"deploy": args.deploy_elasticsearch},
        "kafka": {
            "usePersistentVolume": args.kafka_persistent_volume,
            "kapture_version": kapture_version,
        },
        "loadGen": {"bpsReplicas": args.generators, "kapture_version": kapture_version},
        "postgres": {
            "deploy": args.deploy_postgres,
            "kapture_version": kapture_version,
        },
        "prometheus": {"deploy": args.deploy_prometheus},
        "redis": {"deploy": args.deploy_redis, "kapture_version": kapture_version},
    }

    if args.control_locally:
        import scripts.control.kapture as kap

        os.environ["kapture_config"] = json.dumps(config)
        kap.main()
    else:
        control_namespace = "kapture-control"
        config["control"] = {"namespace": control_namespace, "name": "control"}
        # Make sure that a previous configmap doesn't already exist
        subprocess.call(
            [
                "kubectl",
                "delete",
                "configmap",
                "-n",
                control_namespace,
                "kapture-config",
                "--ignore-not-found",
            ]
        )

        subprocess.call(["kubectl", "create", "ns", control_namespace])
        subprocess.call(
            [
                "kubectl",
                "create",
                "configmap",
                "-n",
                control_namespace,
                "kapture-config",
                "--from-literal",
                "kapture_config={}".format(json.dumps(config)),
            ]
        )

        subprocess.call(["kubectl", "create", "-k", "."])


if __name__ == "__main__":
    main()
