# Kapture

A smoke test repo breaking and diagnosing k8s at large (or small) scales and generating chaos metrics

# Proposed implementation

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
* `./alter-topic.sh db-messages <REPLICA_COUNT>`

To increase the amount of load on the system, run: `kubectl scale --replicas=<REPLICA_COUNT> -f load-gen.yml`

# Future

Our goal over time will be to integrate this with upstreams interested in load testing.

# License

All source in this Repo is Apache Commmons 2.0 licensed, please contribute ideas, code, whatever.  
We'll have prototypes up and running soon.
