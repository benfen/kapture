# Benchmark Results

Listed here are results on running kapture on several differen configurations.  Other markdown files in this folder are stored in the format: `n${node_count}-v${cpu_count}-m${memory}[$any_extra_flags].md`.  For example, a test using three n1-highcpu-4 nodes that had Redis enabled would be called "n3-v12-m11-r.md".

## Method

All tests were run using the [`default-resources.yml`](../../examples/default-resources.yml) configuration.  Tests were run using: `./benchmark.sh $iterations [flags]` (all tests were run in the default mode).  The number of iterations was determined by experimentation.

Output from test runs is placed at `benchmark/temp/results.txt`.  __The benchmark script does not attempt to preserve or protect data from previous runs - it will simply delete any existing data__.

### Troubleshooting

If you run into permissions problems when configuring the Prometheus role bindings, see the [Troubleshooting](https://github.com/carbonrelay/prometheus-recipes#troubleshooting) section of the [prometheus-recipes](https://github.com/carbonrelay/prometheus-recipes) repo that Kapture uses to configure Kapture.

## GKE

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Results |
|-|-|-|-|-|-|-|
| 0.4 | 3 | n1-standard-2 | 6 | 22.50GB | No | [data](./n3-v6-m23.md) |
| 0.4 | 3 | n1-standard-2 | 6 | 22.50GB | Yes | [data](./n3-v6-m23-r.md) |
| 0.4 | 3 | n1-highcpu-4 | 12 | 10.80GB | No | [data](./n3-v12-m11.md) |
| 0.4 | 3 | n1-highcpu-4 | 12 | 10.80GB | Yes | [data](./n3-v12-m11-r.md) |
| 0.4 | 4 | n1-highmem-2 | 8 | 52.00GB | No | [data](./n4-v8-m52.md) |
| 0.4 | 4 | n1-highmem-2 | 8 | 52.00GB | Yes | [data](./n4-v8-m52-r.md) |

## Minikube

The mac book pro used for testing had 8 cores with 16 GB of memory.

| Kapture Version | Nodes | Type | Virtual CPUs | Memory | Redis | Results |
|-|-|-|-|-|-|-|
| 0.4 | 1 | mac book pro | 5 | 8.79GB | No | [data](./n1-v5-m9.md) |
| 0.4 | 1 | mac book pro | 5 | 8.79GB | Yes | [data](./n1-v5-m9-r.md) |