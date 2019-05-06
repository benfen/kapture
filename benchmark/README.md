# Benchmarking

Kapture is a deterministic, realistic workload and the tooling necessary to run it with the click of a button.  The obvious extension of these two components combined is, obviously, a *benchmark*.

In Kapture terms, "Benchmarking" means running kapture on your cluster, to determine how fast and performant it is *relative to other industry standards, i.e. GKE*.  If you are a K8s vendor and would like to submit benchmarks on your own hardware, we'd love to host it, and we can help add it to the benchmarking script.

# Results

Listed here are results on running kapture on several different configurations:

Markdown files are stored in a simple directory layout:

```text
results
 └─ provider1
 └─ provider2
     └─ node_configuration1
     └─ node_configuration2
         └─ 0.json
         └─ 1.json
         └─ 2-r.json
```

Providers are somthing like gke or minikube.  Configurations are listed in the format `${node_count}_${node_type}` and indicate the nodes used.  For example, a configuration using one "standard" node and two "other" nodes, would be called `1_standard_2_other`.  Inside of each configuration are all the runs performed using that configuration.  Each run is name with an increasing index followed (optionally) by any additional configuration flags used.  For example, `2-r.json` indicates a run that had Redis configured.

Kapture is open source, so feel free to reuse this data in other experiements or whitepapers that you might be producing around Kubernetes performance.  Please do cite us though, as we're a new project and are working hard to grow mindshare
and increase contributions from like minded K8's engineers.

## Method

- All tests were run using the [`default-resources.yml`](../examples/default-resources.yml) configuration.  
- Tests were run using: `./benchmark.sh [-r]` (all tests were run with the default speed).  
- If you want more fine-grained control over a test run, try using `./benchmark.sh $iterations [flags]` 
  - This will override the default benchmark heuristic for when to stop.

Output from test runs is placed at `benchmark/temp/results.json` in the same format as the files in the `results` directory. 

__The benchmark script does not attempt to preserve or protect data from previous runs - it will simply delete any existing data__.

### Summary Calculation

The summary value for a benchmarking run was calculated by summing up all the `[2m]` message rates for that run up to the point where performance of Kapture began to noticeably decline.  This value was then averaged over the total number of generators used to reach that point.  For example, if performance degraded after the 3rd load generator, then the summary value could be obtained by summing the `[2m]` messages rate for 1, 2, and 3 load generators and then dividing by 6.  The number of load generators needed to reach this point is presented after the value in parentheses.

### Troubleshooting

- If you run into permissions problems when configuring the Prometheus role bindings, see the [Troubleshooting](https://github.com/carbonrelay/prometheus-recipes#troubleshooting) section of the [prometheus-recipes](https://github.com/carbonrelay/prometheus-recipes) repo that Kapture uses to configure Kapture.

# Characterization

Kapture can attempt to characterize the performance of a cluster based on the past results stored in the `results` directory.  
- To do so as part of a benchmark, run `./benchmark.sh --characterize`.  
- Once the run completes, Kapture will characterize the cluster and spit out the results. 

Note that results for Minikube are not used for characterization, although example data for them does exist.

## What do these results mean?

At the end of the benchmark, it will output something that looks like this:

```text
Score     Provider  Node Configuration           
8.17      gke       3_n1-highcpu-4        
136.11    gke       3_n1-standard-2       
432.89    gke       2_n1-standard-8       
673.88    gke       4_n1-highmem-2 
```

Score is a relative metric, with a lower value indicating that the targeted cluster is more similar to that particular result dataset.  In this example, a gke `3_n1-highcpu-4` cluster has the lowest score, meaning that Kapture thinks the cluster in question is most similar to that sort of cluster.  Results for all known cluster types are output to allow the user to make more informed decisions about the output from Kapture.

Score is a relative metric and should not be compared between different runs of the characterization tool.  It will generally be most useful when comparing cluster types within the same run.

## What if I just want to use the characterization tool?

Easy!  Just go the `benchmark` directory and run the python directly: `python3 characterization.py $result_file $redis`.  `$result_file` should be the path to the result file to scan and `$redis` should be `on` if the result file to scan used Redis.

__This feature should be considered unstable and liable to change in the future__

# Summary of Results

In the summary column, the max number of load generators to produce a decline in performance is listed in parenteheses after the value.

## GKE

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|-|
| 0.4 | 3 | n1-standard-2 | 6 | 22.50GB | No | 66.38 msg/node/s (3) | [data](./results/gke/3_n1-standard-2/0.json) |
| 0.4 | 3 | n1-standard-2 | 6 | 22.50GB | Yes | 62.06 msg/node/s (3) | [data](./results/gke/3_n1-standard-2/1-r.json) |
| 0.4 | 3 | n1-highcpu-4 | 12 | 10.80GB | No | 135.59 msg/node/s (3) | [data](./results/gke/3_n1-highcpu-4/0.json) |
| 0.4 | 3 | n1-highcpu-4 | 12 | 10.80GB | Yes | 125.40 msg/node/s (3) | [data](./results/gke/3_n1-highcpu-4/1-r.json) |
| 0.4 | 4 | n1-highmem-2 | 8 | 52.00GB | No | 91.08 msg/node/s (4) | [data](./results/gke/3_n1-highmem-2/0.json) |
| 0.4 | 4 | n1-highmem-2 | 8 | 52.00GB | Yes | 72.35 msg/node/s (4) | [data](./results/gke/3_n1-highmem-2/1-r.json) |
| 0.4 | 2 | n1-standard-8 | 16 | 60.00GB | No | 122.33 msg/node/s (8) | [data](./results/gke/2_n1-standard-8/0.json) |
| 0.4 | 2 | n1-standard-8 | 16 | 60.00GB | Yes | 103.92 msg/node/s (8) | [data](./results/gke/2_n1-standard-8/1-r.json) |
| 0.4 | 8 | n1-standard-1 | 8 | 30.00GB | Yes | 62.05 msg/node/s (6) | [data](./results/gke/8_n1-standard-1/0-r.json) |

## Minikube

The MacBook Pro used for testing had 8 cores (2.6 GHz Intel Core i7), 16 GB of memory (2400 MHz DDR4), and an SSD.  Minikube itself was run using the [`hyperkit`](https://github.com/kubernetes/minikube/blob/master/docs/drivers.md#hyperkit-driver) driver.

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|-|
| 0.4 | 1 | MacBook Pro | 5 | 8.79GB | No | 134.70 msg/node/s (2) | [data](./results/minikube/0.json) |
| 0.4 | 1 | MacBook Pro | 5 | 8.79GB | Yes | 132.23 msg/node/s (2) | [data](./results/minikube/1-r.json) |
