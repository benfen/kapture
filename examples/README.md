# Example c(K)ustomizations

This directory has examples of how you can modify kapture to suit your needs for differnt performance tests.

These examples are meant to be used with [Kustomize](https://github.com/kubernetes-sigs/kustomize/blob/master/docs/INSTALL.md), but can easily be manually implemented on a kapture fork.

The configuration files in this directory provide some possible configuration to utilize with Kapture.  Three straightforward examples are provided:

* [`default-resources.yml`](./default-resources.yml) - This is the "default" configuration of a Kapture instance.  In general, these options should be considered the base configuration for other approachs.
* [`slow-load-gen.yml`](./slow-load-gen.yml) - This configuration strangles the CPU of the load-gen containers, slowing down the generation of messages, but also delaying the rate that the rest of the cluster runs out of CPU.
* [`unbounded-redis.yml`](./unbounded-redis.yml) - By default, Redis is configured to act as an LRU cache in order to prevent it from slowly consuming all available memory in the cluster.  While this configuration does not remove that specific behavior, it does increase the size of the cache sufficiently to make it seem like there is no eviction strategy.

# How can I use these examples customizations with kapture?

This utilizes Kubernetes built-in [Kustomize][1] functionality to modify existing configurations.  Configurations listed in each example file are merged with the existing configurations in the `kube-config` folder using Kubernetes' built-in merging strategy.

## How do I use it?

Clone this repo

- edit the [`top level kustomization.yml file`](../kustomization.yml) to point to which resource you want. 
- *or* modify it to point to any other multiple kustomizations as well. 
- *or* create your own patches to lay on top of Kapture.  

Run the kapture command line tool the same as you normally would.

## Caveats

* The number of `replicas` should not be modified using [`Kustomize`][1].  The replica count is managed by `Kapture` and should be controlled using the [`kapture.sh`](../kapture.sh) script.  There are a couple of locations in the startup code that depend on the number of replicas (Redis, Kafka) that may not function correctly if these things are modified prior to startup.  Once Kapture initializes, it should be fine to scale things up and down.
* [`redis-master.yml`](../kube-config/redis-master.yml) will not be affected by [`Kustomize`][1] as a consequence of how the clustered Redis needs to start up.

[1]: https://kustomize.io/
