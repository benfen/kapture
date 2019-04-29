# Benchmarking

Listed here are results on running kapture on several differen configurations.  Other markdown files in this folder are stored in the format: `${provider}_${node_type}_n${node_count}_v${cpu_count}_m${memory}_${max_generators}_[$any_extra_flags].md`.  For example, a test using three n1-highcpu-4 nodes from gke that had Redis enabled would be called "`gke_n1-standard-1_n8_v8_m30_6_r.md`".

The value of `max-generators` is determined experimentally and should correspond to the number of generators such that the next generator does not increase the total message throughput.

## Method

All tests were run using the [`default-resources.yml`](../examples/default-resources.yml) configuration.  Tests were run using: `./benchmark.sh $iterations [flags]` (all tests were run with the default speed).  The number of iterations used for each type of cluster was determined by experimentation and extrapolation from previous runs.

Output from test runs is placed at `benchmark/temp/results.txt`.  __The benchmark script does not attempt to preserve or protect data from previous runs - it will simply delete any existing data__.

### Summary Calculation

The summary value for a benchmarking run was calculated by summing up all the `[2m]` message rates for that run up to the point where performance of Kapture began to noticeably decline.  This value was then averaged over the total number of generators used to reach that point.  For example, if performance degraded after the 3rd load generator, then the summary value could be obtained by summing the `[2m]` messages rate for 1, 2, and 3 load generators and then dividing by 6.  The number of load generators needed to reach this point is presented after the value in parentheses.

### Troubleshooting

If you run into permissions problems when configuring the Prometheus role bindings, see the [Troubleshooting](https://github.com/carbonrelay/prometheus-recipes#troubleshooting) section of the [prometheus-recipes](https://github.com/carbonrelay/prometheus-recipes) repo that Kapture uses to configure Kapture.

# Characterization

Kapture can attempt to characterize the performance of a cluster based on the past results stored in the `results` directory.  To do so as part of a benchmark, run `./benchmark.sh $iterations --characterize`.  Once the run completes, Kapture will characterize the cluster and spit out the results.

Python is required for this to function.  If Kapture does not find python (`python3`, `python`, or `py` on the path, specifically) it will simply skip characterization.

## What do these results mean?

At the end of the benchmark, it might output something that looks like this:

```text
Score     Provider  Node Type           
8.17      gke       n1-highcpu-4        
136.11    gke       n1-standard-2       
432.89    gke       n1-standard-8       
673.88    gke       n1-highmem-2 
```

Score is a relative metric, with a lower value indicating that the targeted cluster is more similar.  In this example, a gke `n1-highcpu-4` cluster has the lowest score, meaning that Kapture thinks the cluster in question is most similar to that sort of cluster.  Results for all known cluster types are output to allow the user to make more informed decisions about the output from Kapture.

Because score is a relative metric, it should not be compared between different runs of the characterization tool.  It is only useful when comparing cluster types within the same run.

## What if I just want to use the characterization tool?

Easy!  Just go the `benchmark` directory and run the python directly: `python3 characterization.py $result_file $redis`.  `$result_file` should be the path to the result file to scan and `$redis` should be `on` if the result file to scan used Redis.

__This feature should be considered unstable and liable to change in the future__

# Results

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

The MacBook Pro used for testing had 8 cores with 16 GB of memory.

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Summary | Full Results |
|-|-|-|-|-|-|-|-|
| 0.4 | 1 | MacBook Pro | 5 | 8.79GB | No | 134.70 msg/node/s (2) | [minikube_none_n1_v5_m9.md](./results/minikube_none_n1_v5_m9.md) |
| 0.4 | 1 | MacBook Pro | 5 | 8.79GB | Yes | 132.23 msg/node/s (2) | [minikube_none_n1_v5_m9_r.md](./results/minikube_none_n1_v5_m9_r.md) |
