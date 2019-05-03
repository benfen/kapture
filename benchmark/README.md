# Benchmarking

Kapture is a deterministic, realistic workload and the tooling necessary to run it with the click of a button.  The obvious extension of these two components combined is, obviously, a *benchmark*.

In Kapture terms, "Benchmarking" means running kapture on your cluster, to determine how fast and performant it is *relative to other industry standards, i.e. GKE*.  If you are a K8s vendor and would like to submit benchmarks on your own hardware, we'd love to host it, and we can help add it to the benchmarking script.

# Results

Listed here are results on running kapture on several different configurations:

Other markdown files in this folder are stored in the format: `${provider}_${node_type}_n${node_count}_v${cpu_count}_m${memory}_${max_generators}_[$any_extra_flags].md`.  For example, a test using three n1-highcpu-4 nodes from gke that had Redis enabled would be called "`gke_n1-standard-1_n8_v8_m30_6_r.md`".

The value of `max-generators` is determined experimentally and should correspond to the number of generators such that the next generator does not increase the total message throughput.  By default, this is the point at which the `benchmark.sh` will exit.

Kapture is open source, so feel free to reuse this data in other experiements or whitepapers that you might be producing around Kubernetes performance.  Please do site us though, as we're a new project and are working hard to grow mindshare
and increase contributions from like minded K8's engineers.

## Method

- All tests were run using the [`default-resources.yml`](../examples/default-resources.yml) configuration.  
- Tests were run using: `./benchmark.sh [-r]` (all tests were run with the default speed).  
- If you want more fine-grained control over a test run, try using `./benchmark.sh $iterations [flags]` 
- This will override the default benchmark heuristic for when to stop.

Output from test runs is placed at `benchmark/temp/results.txt` in the same format as the file in the `results` directory. 

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

Python is required for this to function.  If Kapture does not find python (`python3`, `python`, or `py` on the path, specifically) it will simply skip characterization.

## What do these results mean?

At the end of the benchmark, it will output something that looks like this:

```text
Score     Provider  Node Type           
8.17      gke       n1-highcpu-4        
136.11    gke       n1-standard-2       
432.89    gke       n1-standard-8       
673.88    gke       n1-highmem-2 
```

Score is a relative metric, with a lower value indicating that the targeted cluster is more similar to that particular result dataset.  In this example, a gke `n1-highcpu-4` cluster has the lowest score, meaning that Kapture thinks the cluster in question is most similar to that sort of cluster.  Results for all known cluster types are output to allow the user to make more informed decisions about the output from Kapture.

Score is a relative metric and should not be compared between different runs of the characterization tool.  It will generally be most useful when comparing cluster types within the same run.

## What if I just want to use the characterization tool?

Easy!  Just go the `benchmark` directory and run the python directly: `python3 characterization.py $result_file $redis`.  `$result_file` should be the path to the result file to scan and `$redis` should be `on` if the result file to scan used Redis.

__This feature should be considered unstable and liable to change in the future__

# Summary of Results

In the summary column, the max number of load generators to produce a decline in performance is listed in parenteheses after the value.

## GKE

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|-|
| 0.4 | 3 | n1-standard-2 | 6 | 22.50GB | No | 66.38 msg/node/s (3) | [gke_n1-standard-2_n3_v6_m23_3.md](./results/gke_n1-standard-2_n3_v6_m23_3.md) |
| 0.4 | 3 | n1-standard-2 | 6 | 22.50GB | Yes | 62.06 msg/node/s (3) | [gke_n1-standard-2_n3_v6_m23_3_r.md](./results/gke_n1-standard-2_n3_v6_m23_3_r.md) |
| 0.4 | 3 | n1-highcpu-4 | 12 | 10.80GB | No | 135.59 msg/node/s (3) | [gke_n1-highcpu-4_n3_v12_m11_3.md](./results/gke_n1-highcpu-4_n3_v12_m11_3.md) |
| 0.4 | 3 | n1-highcpu-4 | 12 | 10.80GB | Yes | 125.40 msg/node/s (3) | [gke_n1-highcpu-4_n3_v12_m11_3_r.md](./results/gke_n1-highcpu-4_n3_v12_m11_3_r.md) |
| 0.4 | 4 | n1-highmem-2 | 8 | 52.00GB | No | 91.08 msg/node/s (4) | [gke_n1-highmem-2_n4_v8_m52_4.md](./results/gke_n1-highmem-2_n4_v8_m52_4.md) |
| 0.4 | 4 | n1-highmem-2 | 8 | 52.00GB | Yes | 72.35 msg/node/s (4) | [gke_n1-highmem-2_n4_v8_m52_4_r.md](./results/gke_n1-highmem-2_n4_v8_m52_4_r.md) |
| 0.4 | 2 | n1-standard-8 | 16 | 60.00GB | No | 122.33 msg/node/s (8) | [gke_n1-standard-8_n2_v16_m60_8.md](./results/gke_n1-standard-8_n2_v16_m60_8.md) |
| 0.4 | 2 | n1-standard-8 | 16 | 60.00GB | Yes | 103.92 msg/node/s (8) | [gke_n1-standard-8_n2_v16_m60_8_r.md](./results/gke_n1-standard-8_n2_v16_m60_8_r.md) |
| 0.4 | 8 | n1-standard-1 | 8 | 30.00GB | Yes | 62.05 msg/node/s (6) | [gke_n1-standard-1_n8_v8_m30_6.md](./results/gke_n1-standard-1_n8_v8_m30_6.md)

## Minikube

The MacBook Pro used for testing had 8 cores (2.6 GHz Intel Core i7), 16 GB of memory (2400 MHz DDR4), and an SSD.  Minikube itself was run using the [`hyperkit`](https://github.com/kubernetes/minikube/blob/master/docs/drivers.md#hyperkit-driver) driver.

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|-|
| 0.4 | 1 | MacBook Pro | 5 | 8.79GB | No | 134.70 msg/node/s (2) | [minikube_none_n1_v5_m9.md](./results/minikube_none_n1_v5_m9.md) |
| 0.4 | 1 | MacBook Pro | 5 | 8.79GB | Yes | 132.23 msg/node/s (2) | [minikube_none_n1_v5_m9_r.md](./results/minikube_none_n1_v5_m9_r.md) |
