# Kapture: Realistic cluster benchmarking for Cloud Native Application developers

If you build applications or ship kubernetes products, you need a way to determine wether or not the infrastructure is causing problems for you.  One way to do this is running the kubernetes end to end tests, but that only tells you about functionality.  Another option would be to run Kubernetes performance tests, however, these tend to measure different metrics in isolation.  Kapture fills the gap: demonstrating giving you a realistic performance benchmark, based on a realistic workload.

If you're new to performance and load testing on kubernetes... check out our [recent demo of the first Kapture demo for Sig Big Data](https://zoom.us/recording/play/e1GXJ5V4DHLkSShbdeJCQwNg_m4icnLcAD_O0rX6xLb71n635GyaqK3ehc7Pr4bm?startTime=1556730127000) which provides a comprehensive introduction to this project.

## What's is a realistic workload?

A production SaaS or Data center cluster will feature a broad range of workloads, often many of them using different resource
sharing and access patterns.  Kapture simulates one such production in environment: the enterprise data driven application
stack.  As an example, below is a screenshot of a Kapture run on a single node cluster, where you can observe several different
types of oscillating resource consumption patterns.

<!-- <a href="https://asciinema.org/a/ujJ5BrANN5cRFfl8hTPm4zT5X
"><img src="https://asciinema.org/a/ujJ5BrANN5cRFfl8hTPm4zT5X.png" width="836"/></a> -->

## Kapture Tutorial

If you're interested in a more complete walkthrough of Kapture's capabilities, be sure to check out the tutorial!

[![Kapture Tutorial](https://i.ytimg.com/vi/ZZbEvMRrf90/hqdefault.jpg?sqp=-oaymwEjCNACELwBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLCimMzNU8LwFqEe7TLRZNiod-myhA)](https://www.youtube.com/watch?v=ZZbEvMRrf90&t=4s)

## Quick Start !!!

In any case, give it a shot on your kubernetes cluster - you may learn something about the durability and reliability
of your networking, storage, and virtualization layers.  Better yet, you might learn a little bit about how multi-tier
applications are deployed in a real kubernetes environment.  

Its easy !

```
./kapture.sh perf-test 3 -erp # run kapture in the perf-test namespace, with a relative scale of 3 replicas and using elasticsearch, redis and prometheus
``` 

And compare your results to the data in the [benchmarks](https://github.com/carbonrelay/kapture/tree/master/benchmark/results).

See the `kube-config` directory for details of what was created.

## Project Goals

- To build a a ridiculously easy to use, easy to K8s hack load generator focused on the bigdata and NoSQL community: No vanity languages required.
- To curate a generic tool that pushes the limits of all major cluster resources in a deterministic way.
- To simulate the behaviour of these apps under realistic workloads, at scale, of the common 'lift and shift' kuberentes enterprise experience.  Some of these behaviors might include:
  - Jvm apps that make their own app frameworks inside other frameworks, b/c they were designed in the 1990s.
  - Ruby apps with tons and tons of code and memory getting slurped up for no reason.
  - Web apps with weird transaction flows b/c you didn't batch properly.
  - Message queues that never seem to end, and users that can't make up their minds.

However, our current load generator is based on an extremely realistic data generator, [BigPetStore](https://github.com/apache/bigtop/tree/master/bigtop-bigpetstore), which in and of itself simluates
resource usage patterns that are very hard to build in a one off manner.

Currently our architecture is heavily based on *kafka*, but includes several other NoSQL technologies, including redis, elasticsearch, and zookeeper.  We are open to ideas on including other technologies as well ! Kapture is sufficiently resilient due to its kafka baseline such that it can easily support other snowflake applications.

# Kapture data flow

This is only partially implemented as of April 30, 2019. The Postgres Mongo spout and the webapp running in front of Kapture are remaining.  We'll update this shortly !

```
  Kafka <--- Generated BPS (or other) transactions <--------------- Webapp ----+
  / \ |                                                                        |
   |   |                                                   + ------> Redis <---+
   |   |                                                   |
   |   +-----> topic (massachusets)---> |                  |
   |   +-----> topic (california)  ---> | --> ETL [Spark, or just a script]
   |   +-----> topic (texas)       ---> |                  |
   |                                                       |
   |                                                       |
   -------------------Postgres/Mongo <---------------------+
```

# Benchmarks

Take a look at the [`data`](benchmark/README.md)!

# Detailed Usage

## Your first time ?

As shown eariler, to run kapture, just download this repo, cd to it, and run it.
If you want to tune the simulation parameters for the input data generators, or what components are processing them, just run

```
./kapture.sh --help
```

to get a list of all the configuration options for `kapture.sh`.

### Deploying Redis

By default, Kapture doesn't deploy Redis as part of its minimalistic approach.  If you want to include Redis as part of your deployment, just run `./kapture.sh kapture-spam-my-namespace 3 --deploy-redis`.  That will start up Kapture with a clustered Redis configuration that listens to Kafka for messages.

### Deploying ElasticSearch

Elasticsearch operates in the same manner as Redis - if you want to deploy Elasticsearch just run `./kapture.sh kapture-spam-my-namespace 3 --deploy-elastic-search` to get Kapture running with a basic Elasticsearch configuration.

## How do I scale up the load?

To increase the amount of load on the system, run: `kubectl scale Deployment data-loader --replicas $REPLICA_COUNT -n kapture-spam-my-namespace`.

## What if I want to test a more advanced scenario ?

Kapture is not overengineered to support a myriad of situations.  We expect engineers and developers to
use this framework and modify the YAMLs as required.  Out of the box it does one thing, very well: generate
realistic load for an enterprise grade application with a message queue and scalable key value store.

## So, what if you want to do something more advanced ?

Hack it ! The YAML recipes are all in this repository so that you can build your own new tests on top of
kapture.  Over time, please do file issues if you feel strongly that we should modularize/helmify our deployments
to support a broader range of test types.

The possibilities are endless !

### Example Kapture projects to create new load tests

- Modify the kafka volumes to use persistent storage. (note we probably will support this soon.. not sure yet though).
- Increase the CPU and Memory parameters for Kafka
- Change the memory foot print or scaling factor of Redis
- Add a different load generator container than BigPetStore

### Can I Kustomize my Kapture?

You bet!  Check out the [`examples`](examples/README.md) for how you can use [`Kustomize`][1] to create all kinds of different configurations for Kapture!

## What if want Prometheus metrics?

Kapture's got it!  Just head over to [prometheus-recipes](https://github.com/carbonrelay/prometheus-recipes) and apply the `basic` cofiguration to your cluster.  Make sure to use the same namespace when configuring your cluster for prometheus as you do for Kapture.  For reference, Kapture's [benchmark tool](benchmark/README.md) configures a cluster with `./prometheus-recipes.sh -npk` to get the node level metrics that it needs.

Once that has been done, you can configure your cluster to provide metrics to prometheus by running `./kapture.sh kapture-spam-my-namespace -p`.  It's that easy!

## How do I clean my cluster up?

Just run `./kapture.sh kapture-spam-my-namespace --delete`!  Kapture will take care of the rest.

# WHY IS THIS JAVA EVERYTHING RELATED TO CONTAINERS SHOULD BE GO WHAT IS WRONG WITH YOU

As popular as Golang is in the infrastructure universe, the fact is that enterprises ship Java code at massive scales,
and the goal of Kapture is to simulate enterprise enviornments for upstream kubernetes load and scale testing.

So, yeah, we've got some java in here.

The goal of Kapture is tightly focused on simulating enterprise kubernetes applications at large scales, anything
largely outside of that relm, including generic load testing for performance SLAs and so on, might be more well
serviced by other scale and density tests in the upstream Kuberentes community.

# Future

- Dockerization of the kapture container with
  - kubectl (poor mans operator)
  - gradle : to build kafka connectors
  - jvm : to support running bps, gradle, etc

# License

All source in this Repo is Apache Commmons 2.0 licensed, please contribute ideas, code, whatever.  It would be awesome if,
eventually we were able to support 10 or 15 different databases.

[1]: https://kustomize.io/
