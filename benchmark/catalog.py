import shutil
import json
import subprocess
import os


def get_node_statistics():
    """Fetches node information for a cluster

    Returns:
        A tuple in the form (provider, nodes, cpu, memory) where
            provider - Name of the cluster provider (e.g. gke)
            nodes - A dict mapping the name of the type of node to the count of that node
            cpu - Total amount of cpus in the cluster
            memory - Total amount of memory (in GB) in the cluster
    """
    node_data = json.loads(
        subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
    )

    if "gke" in node_data["items"][0]["metadata"]["name"]:
        provider = "gke"
    else:
        provider = "minikube"

    if provider == "minikube":
        cpu = node_data["items"]["status"]["capacity"]["cpu"]
        memory = round(
            int(node_data["items"]["status"]["capacity"]["memory"].rstrip("Ki"))
            / 1024 ** 2,
            2,
        )
        nodes = {"minikube": 1}
    else:
        cpu = 0
        memory = 0
        nodes = {}

        for node in node_data["items"]:
            cpu += int(node["status"]["capacity"]["cpu"])
            memory += int(node["status"]["capacity"]["memory"].rstrip("Ki"))
            label = node["metadata"]["labels"]["beta.kubernetes.io/instance-type"]
            if label in nodes:
                nodes[label] += 1
            else:
                nodes[label] = 1

        memory = round(memory / 1024 ** 2, 2)

    return (provider, nodes, cpu, memory)


def get_config_identifier(nodes):
    """Generate an identifer for a configuration of nodes

    Takes in a list of nodes within a cluster and generates a consistent identifier for that configuration.

    Args:
        nodes - Dict mapping node names (e.g. n1-standard-2) to the number of nodes of that type present in the cluster

    Returns:
        A string identifier for the node configuration of the cluster
    """
    name = ""
    for node in sorted(nodes.keys()):
        name += "{}_{}_".format(nodes[node], node)

    return name.rstrip("_")


def append_to_catalog(data_path, result_dir):
    """Updates the data in the results directory

    Takes in data stored in the result path and uses that to update the catalog as well as the other data
    stored in the result directory.

    Args:
        data_path - Path to the file containing data for the run to be added to the catalog
        result_dir - Path to the directory containing the results
    """
    catalog_path = os.path.join(result_dir, "catalog.json")
    with open(data_path) as r, open(catalog_path) as c:
        catalog = json.load(c)
        results = json.load(r)

    old_messages = 0
    summary = 0
    max = 0
    for counter, item in enumerate(results["data"]):
        if item["messages"] > old_messages:
            summary += item["messages"]
            old_messages = item["messages"]
            max = counter + 1

    summary /= max * (max + 1) / 2
    node_stats = get_node_statistics()

    for provider in catalog:
        # Currently do not support adding extra providers automatically
        if node_stats[0] == provider["provider"]:
            item = None
            runs = 0
            for config in provider["data"]:
                if (
                    config["nodes"] == node_stats[1]
                    and config["configuration"] == results["configuration"]
                ):
                    item = config
                    runs = len(item["runs"])
                    break

            flag_string = "-"
            if results["configuration"]["redis"]:
                flag_string += "r"
            flag_string.rstrip("-")

            run = {
                "path": os.path.join(
                    node_stats[0],
                    get_config_identifier(node_stats[1]),
                    "{}{}.json".format(runs, flag_string),
                ),
                "max": max,
                "summary": summary,
            }

            if item is not None:
                item["summary"] = (item["summary"] * runs + summary) / (runs + 1)
                item["runs"].append(run)
            else:
                item = {
                    "nodes": node_stats[1],
                    "configuration": results["configuration"],
                    "cpus": node_stats[2],
                    "memory": node_stats[3],
                    "summary": summary,
                    "runs": [run],
                }
                provider["data"].append(item)

            output_file = os.path.join(result_dir, run["path"])
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            shutil.copyfile(data_path, output_file)
            with open(catalog_path, "w") as c:
                json.dump(catalog, c, sort_keys=True, indent=4)
