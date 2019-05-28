from argparse import ArgumentParser
import json
import subprocess


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
        "-e",
        "--deploy-elasticsearch",
        action="store_true",
        help="Deploy elasticsearch and logstash as part of Kapture",
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
    parser.add_argument(
        "--load-gen-count",
        dest="generators",
        help="Number of load generators to create to place load on the cluster",
    )
    args = parser.parse_args()

    if args.delete:
        action = "delete"
    else:
        action = "create"
    config = {
        "action": action,
        "namespace": args.namespace,
        "control": {"namespace": "kapture-control", "name": "control"},
        "elasticsearch": {"deploy": args.deploy_elasticsearch},
        "kafka": {"usePersistentVolume": False},
        "loadGen": {"bpsReplicas": args.generators},
        "postgres": {"deploy": args.deploy_postgres},
        "prometheus": {"deploy": args.deploy_prometheus},
        "redis": {"deploy": args.deploy_redis},
    }

    control_namespace = "kapture-control"
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

    if not args.delete:
        subprocess.call(['kubectl', 'create', 'ns', control_namespace])
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

        subprocess.call(["kubectl", "create", "-f", "kapture.yml"])
    else:
        subprocess.call(["kubectl", "delete", "-f", "kapture.yml"])


if __name__ == "__main__":
    main()
