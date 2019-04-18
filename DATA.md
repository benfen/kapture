# Test Data

Basic testing for this was done on a GKE cluster with 2 nodes, 8 vCPUs, and 30G of memory.  In order to test the cluster, the load generation was scaled up one at a time.  The health of the cluster was monitored using the prometheus metrics for transactions/second (both from the kafka subscription and from kafka itself) over the course of a minute as well as the resource utilization of the cluster.

__These tests were performed on v0.2 with default configurations.  Results may change considerably with Kapture over time.__

| Load generators | Transactions/second (GKE) | Transactions/second (Minikube on CentOS w/ kvm2 driver) |
|---|---|---|
| 1 | ~150 | ~210 |
| 2 | ~300 | ~420 |
| 3 | ~420 | ~620 |
| 4 | ~590 | ~800 |
| 5 | ~620 | ~960 |
| 6 | ~640 | ~1130 |
| 7 | ~460-800 (exceptionally varied) | ~1320 (varied)  |
| 8 | ~550-820 (exceptionally varied) | ~670-1240 (expectionally varied) |

In general, testing seems to display two separate slowdowns.  The first occurs when the CPU of the cluster starts to become insufficient due to the load generators.  In the example here, that seems to occur around 6 load generators.  At this point, the number of transactions begins to decline due to resource starvation, although the metrics for it begin to vary wildly.  Observing the CPU utilization of the cluster also shows that it starts to hover around 90% consistently.  Past 8 load generators, metrics are hard to trust due to variance displayed.

At 11 load generators the entire cluster begins to experience acute memory pressure and nodes start getting evicted.  This is the point where the cluster is basically becoming unusable.  Adding more load generators past this point will make the problem worse, but it's not a very noticeable difference.  It is worth noting that, although slow, Redis will eventually also begin to run the cluster out of memory, as there is no recycling strategy.
