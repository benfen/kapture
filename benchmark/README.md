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
         └─ 0-r.json
```

Providers are somthing like gke or minikube.  Configurations are listed in the format `${node_count}_${node_type}` and indicate the nodes used.  For example, a configuration using one "standard" node and two "other" nodes, would be called `1_standard_2_other`.  Inside of each configuration are all the runs performed using that configuration.  Each run is name with an increasing index followed (optionally) by any additional configuration flags used.  For example, `0-r.json` indicates a run that had Redis configured.

Kapture is open source, so feel free to reuse this data in other experiements or whitepapers that you might be producing around Kubernetes performance.  Please do cite us though, as we're a new project and are working hard to grow mindshare
and increase contributions from like minded K8's engineers.

## Method

- Tests were run using: `./benchmark.sh [-r]`
- If you want more fine-grained control over a test run, try using `./benchmark.sh $iterations [flags]` 
  - This will override the default benchmark heuristic for when to stop.

Output from test runs is placed at `benchmark/temp/results.json` in the same format as the files in the `results` directory.  There is a second file located next to this called `updates.json`.  This file is periodically updated with results from the run whenever the load generators are scaled __or__ if you have enabled the `heartbeat` configuration option, it will be updated approximately every `n` seconds.

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

| Node Configuration | Virtual CPUs | Memory | Elasticsearch | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|
| 3_n1-highmem-4 | 12 | 78.0GB | No | No | 1038.82 msg/node/s | [0](./results/gke/3_n1-highmem-4/0.json) |
| 3_n1-standard-2 | 8 | 30.0GB | No | No | 863.6702962989389 msg/node/s | [0](./results/gke/3_n1-standard-2/0.json), [1](./results/gke/3_n1-standard-2/1.json), [2](./results/gke/3_n1-standard-2/2.json), [3](./results/gke/3_n1-standard-2/3-.json) |
| 4_n1-standard-4 | 12 | 45.0GB | No | No | 1116.66 msg/node/s | [0](./results/gke/4_n1-standard-4/0.json) |
| 4_n1-highcpu-4 | 16 | 14.4GB | No | No | 1109.19 msg/node/s | [0](./results/gke/4_n1-highcpu-4/0.json) |
| 4_n1-standard-2 | 8 | 30.0GB | No | No | 909.64 msg/node/s | [0](./results/gke/4_n1-standard-2/0.json), [1](./results/gke/4_n1-standard-2/1.json) |
| 4_n1-standard-2 | 8 | 30.0GB | No | Yes | 669.87 msg/node/s | [0](./results/gke/4_n1-standard-2/0-r.json) |
| 3_n1-standard-2 | 6 | 21.91GB | No | Yes | 907.0176249002939 msg/node/s | [0](./results/gke/3_n1-standard-2/0-r.json) |
| 3_n1-standard-2 | 6 | 21.91GB | Yes | No | 328.7200701259236 msg/node/s | [0](./results/gke/3_n1-standard-2/0-e.json), [1](./results/gke/3_n1-standard-2/1-e.json), [2](./results/gke/3_n1-standard-2/2-e.json) |
| 3_n1-standard-2 | 6 | 21.91GB | Yes | Yes | 892.1910102985422 msg/node/s | [0](./results/gke/3_n1-standard-2/0-er.json), [1](./results/gke/3_n1-standard-2/1-er.json) |
| 8_n1-standard-1 | 8 | 28.9GB | No | No | 242.437809926113 msg/node/s | [0](./results/gke/8_n1-standard-1/0.json), [1](./results/gke/8_n1-standard-1/1.json) |
| 3_n1-highcpu-4 | 12 | 10.39GB | No | No | 1076.8819670369332 msg/node/s | [0](./results/gke/3_n1-highcpu-4/0.json), [1](./results/gke/3_n1-highcpu-4/1.json), [2](./results/gke/3_n1-highcpu-4/2.json) |
| 2_n1-highcpu-4_2_n1-highmem-4_2_n1-standard-2 | 20 | 72.56GB | No | No | 1001.47627557153 msg/node/s | [0](./results/gke/2_n1-highcpu-4_2_n1-highmem-4_2_n1-standard-2/0.json), [1](./results/gke/2_n1-highcpu-4_2_n1-highmem-4_2_n1-standard-2/1.json), [2](./results/gke/2_n1-highcpu-4_2_n1-highmem-4_2_n1-standard-2/2.json) |

## Minikube

The MacBook Pro used for testing had 8 cores (2.6 GHz Intel Core i7), 16 GB of memory (2400 MHz DDR4), and an SSD.  Minikube itself was run using the [`hyperkit`](https://github.com/kubernetes/minikube/blob/master/docs/drivers.md#hyperkit-driver) driver.

| Node Configuration | Virtual CPUs | Memory | Elasticsearch | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|
| 1_MacBookPro | 5 | 8.20GB | No | No | 1279.47 msg/node/s (3) | [data](./results/minikube/0.json) |
