# Kapture

Kapture is an open source smoke testing and load generation tool based on modern application architectures, which typically combine N microservices against a durable message queue.

It is meant to be an 'infrastructure centric' implementation of the original bigpetstore paper, which largely
focuses on generating large amounts of streaming data w/ the apache bigtop project.

However, its current load generator is very primitive, and is bash based.

# Kapture data flow

This is only partially implemented as of April 4, 2019. The Postgres Mongo spout as well as the 
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

# Usage

The method for generating load and attempt to mess with Kubernetes currently uses shell scripts, specifically Bash.  If you are not running this on Linux, there may be issues using those scripts.

To use this repo, the containers for this kubernetes need to be added to the cluster.  To do that, create the containers for the kapture in your cluster:
* `kubectl create -f zk.yml`
* `kubectl create -f kafka.yml`
* `kubectl create -f redis.yml`
* `kubectl create -f rk-conn.yml`

This will create a zookeeper instance, a couple kafka instances to talk to that, a redis that's just kind of there, and a quick container to serve as the link between redis and kafka.

Once the cluster is configured, generate load by starting up the load generator: `kubectl create -f load-gen.yml`

## Scaling

Right now, both Kafka and the load generator can be scaled up.  To scale up Kafka:
* `kubectl scale --replicas=<REPLICA_COUNT> -f kafka.yml`
* `./scripts/alter-topic.sh db-messages <REPLICA_COUNT>`

To increase the amount of load on the system, run: `kubectl scale --replicas=<REPLICA_COUNT> -f load-gen.yml`

# WHY IS THIS JAVA ?

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
