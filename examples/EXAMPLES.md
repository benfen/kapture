# Examples

The configuration files in this directory provide some possible configuration to utilize with Kapture.  Three straightforward examples are provided:

* [`default-resources.yml`](./default-resources.yml) - This is the "default" configuration of a Kapture instance.  In general, these options should be considered the base configuration for other approachs.
* [`slow-load-gen.yml`](./slow-load-gen.yml) - This configuration strangles the CPU of the load-gen containers, slowing down the generation of messages, but also delaying the rate that the rest of the cluster runs out of CPU.
* [`unbounded-redis.yml`](./unbounded-redis.yml) - By default, Redis is configured to act as an LRU cache in order to prevent it from slowly consuming all available memory in the cluster.  While this configuration does not remove that specific behavior, it does increase the size of the cache sufficiently to make it seem like there is no eviction strategy.

# How does it work?

This utilizes Kubernetes built-in [Kustomize][1] functionality to modify existing configurations.  Configurations listed in each example file are merged with the existing configurations in the `kube-config` folder using Kubernetes' built-in merging strategy.

## How do I use it?

Just modify the [`kustomization.yml`](../kustomization.yml) to point to which resource you want.  Or modify it to point to multiple resources.  Or create your own patches to lay on top of Kapture.  Do whatever you want!

## Caveats

* With the exception of [`zk.yml`](../kube-config/zk.yml) and [`kafka.yml`](../kube-config/kafka.yml), the number of `replicas` should not be modified using [`Kustomize`][1].  The replica count is managed by `Kapture` and should be controlled using the [`kapture.sh`](../kapture.sh) script.
* Neither [`rk-conn.yml`](../kube-config/rk-conn.yml) nor [`redis-master.yml`](../kube-config/redis-master.yml) will be affected by [`Kustomize`][1].

[1]: https://kustomize.io/
