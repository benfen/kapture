# Is my K8s cluster capable of supporting production workloads ? 

Find out by running this:

```
NS=perf-test \
REPLICAS=1 \
./kapture.sh $NS $REPLICAS
```

And compare your results to the data in the (benchmarks)[https://github.com/carbonrelay/kapture/tree/master/benchmark/results]. 

See the `kube-config` directory for details of what was created.

## What did I just do ? 

You just ran Kapture !  Kapture is a load generator / application simulator for K8s based on the enterprise development model.

## Whats Kapture? 

- A ridiculously easy to use, easy to hack load generator: No vanity languages required.  It is meant to simulate the behaviour, at scale, of the common 'lift and shift' kuberentes enterprise experience.
  - Jvm apps that make their own app frameworks inside other frameworks, b/c they were designed in the 1990s.
  - Ruby apps with tons and tons of code and memory getting slurped up for no reason.
  - Web apps with weird transaction flows b/c you didn't batch properly.
  - Message queues that never seem to end, and users that can't make up their minds.
- Understandable to anyone that builds apps.
- Gauranteed to push the limits of all major cluster resources in a deterministic way.

# Kapture

Kapture is an open source smoke testing and load generation tool based on modern application architectures, which typically combine N microservices against a durable message queue.

It is meant to be an 'infrastructure centric' implementation of the original bigpetstore paper, which largely
focuses on generating large amounts of streaming data w/ the apache bigtop project.

However, its current load generator is very primitive, and is still being fleshed out.

# Kapture data flow

This is only partially implemented as of April 18, 2019. The Postgres Mongo spout as well as the 
fine grained topics are remaining.  We'll update this shortly !

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

# Usage

## Your first time ?
 
To run kapture, just download this repo, cd to it, and run:
```
./kapture.sh kapture-spam-my-namespace 3
```

That's it!  This will create a single load store generation that will write to various kafka topics.  It will trigger a wide variety of JVM, disk, Memory, and I/O patterns proportional to the number of load generators, i.e., the number of petstore transactions which are generated.

For further configuration, try running `./kapture.sh --help` to see other configuration options specifics to the BigPetStore implementation.

### Deploying Redis

By default, Kapture doesn't deploy Redis as part of its minimalistic approach.  If you want to include Redis as part of your deployment, just run `./kapture.sh kapture-spam-my-namespace 3 --deploy-redis`.  That will start up Kapture with a basic Redis configuration that listens to Kafka for messages.

## How do I scale up the load?

Right now, Kafka, Redis, and the load generator can be scaled up.  To scale up Kafka: `kubectl scale StatefulSet kafka --replicas=$REPLICA_COUNT -n kapture-spam-my-namespace`

To scale Redis, just run `kubectl scale --replicas=$REPLICA_COUNT rc redis -n kapture-spam-my-namespace`!

To increase the amount of load on the system, run: `kubectl scale Deployment data-loader --replicas $REPLICA_COUNT -n kapture-spam-my-namespace`

## What if I want to test a more advanced scenario ?

Kapture is not overengineered to support a myriad of YAML situations.  We expect engineers and developers to 
use this framework and modify the YAMLs as required.  Out of the box, it does one thing, very well: Generating
realistic load for an enterprise grade application with a message queue and scalable key value store.

## So, what if you want to do something more advanced ?

Hack it ! The YAML recipes are all in this repository so that you can build your own new tests on top of 
kapture.  Over time, please do file issues if you feel strongly that we should modularize/helmify our deployments
to support a broader range of test types.

The possibilities are endless !

### Can I Kustomize my Kapture?

You bet!  Check out the [`examples`](examples/README.md) for how you can use [`Kustomize`][1] to create all kinds of different configurations for Kapture!

## What if want Prometheus metrics?

Kapture's got it!  Just head over to [prometheus-recipes](https://github.com/carbonrelay/prometheus-recipes) and apply the `basic` cofiguration to your cluster.  Make sure to use the same namespace when configuring your cluster for prometheus as you do for Kapture.

Once that has been done, you can configure your cluster to provide metrics to prometheus by running `./kapture.sh kapture-spam-my-namespace -p`.  It's that easy!

## How do I clean my cluster up?

Just run `./kapture.sh kapture-spam-my-namespace --delete`!  Kapture will take care of the rest.

### Example Kapture projects to create new load tests

- Modify the kafka volumes to use persistent storage. (note we probably will support this soon.. not sure yet though).
- Increase the CPU and Memory parameters for Kafka
- Change the memory foot print or scaling factor of Redis
- Add a different load generator container than BigPetStore

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

All source in this Repo is Apache Commmons 2.0 licensed, please contribute ideas, code, whatever.  
We'll have prototypes up and running soon.

# Dev policy

- Push to master
- Accept almost any PR, this is a work in progress
- Ideas that are half baked : Merge them to contrib/ :)

[1]: https://kustomize.io/
