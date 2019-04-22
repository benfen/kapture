#!/bin/bash

# m4_ignore(
echo "This is just a script template, not the script (yet) - pass it to 'argbash' to fix this." >&2
exit 11  #)Created by argbash-init v2.8.0
# Rearrange the order of options below according to what you would like to see in the help message.
# ARG_OPTIONAL_SINGLE([stores],[s],[Number of stores to initialize the BigPetStore with.  Will correspond to the number of Kafka topcis that will be generated],[250])
# ARG_OPTIONAL_SINGLE([customers],[c],[Number of customers to simulate for BigPetStore],[5000])
# ARG_OPTIONAL_SINGLE([simulation],[d],[Time (in days) to run the BigPetStore simulation over],[1500]))
# ARG_OPTIONAL_SINGLE([redis-count],[],[Number of Redis instances to cluster.  This option will be ignored unless deploy-redis is set to true.],[3]))
# ARG_OPTIONAL_BOOLEAN([delete], [], [Deletes all the kubernetes resources generated by a normal run], [off])
# ARG_OPTIONAL_BOOLEAN([deploy-prometheus], [p], [Deploy Prometheus as part of the cluster.  At this time, this option should be considered experimental and not fully functional.], [off])
# ARG_OPTIONAL_BOOLEAN([deploy-redis], [r], [Deploy Redis (and the connector) as part of the cluster], [off])
# ARG_OPTIONAL_BOOLEAN([deploy-elastic-search], [e], [Deploy Elastic search (and the connector) as part of the cluster], [off])
# ARG_POSITIONAL_SINGLE([namespace],[The namespace to deploy Kapture to],[])
# ARG_POSITIONAL_SINGLE([load-gen-count],[Number of load generators to create to place load on the cluster],[0])
# ARG_DEFAULTS_POS
# ARG_HELP([This script configures a cluster to run Kapture.])
# ARGBASH_GO

# [ <-- needed because of Argbash

printf 'Value of --%s: %s\n' 'stores' "$_arg_stores"
printf 'Value of --%s: %s\n' 'customers' "$_arg_customers"
printf 'Value of --%s: %s\n' 'simulation' "$_arg_simulation"
printf "'%s' is %s\\n" 'delete' "$_arg_delete"
printf "'%s' is %s\\n" 'deploy-prometheus' "$_arg_deploy_prometheus"
printf "'%s' is %s\\n" 'deploy-redis' "$_arg_deploy_redis"
printf "'%s' is %s\\n" 'deploy-elastic-search' "$_arg_deploy_elastic_search"
printf "Value of '%s': %s\\n" 'namespace' "$_arg_namespace"
printf "Value of '%s': %s\\n" 'load-gen-count' "$_arg_load_gen_count"
printf "Value of '%s': %s\\n" 'redis-count' "$_arg_redis_count"

# ] <-- needed because of Argbash

export namespace=$_arg_namespace
export load_generators=$_arg_load_gen_count
export redis_count=$_arg_redis_count
export customers=$_arg_customers
export simulation_time=$_arg_simulation
export stores=$_arg_stores
export deploy_prometheus=$_arg_deploy_prometheus
export deploy_redis=$_arg_deploy_redis
export deploy_elastic_search=$_arg_deploy_elastic_search
export delete=$_arg_delete

./scripts/kapture.sh
