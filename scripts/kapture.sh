BASEDIR=$(dirname $0)

function exit_if_bad() {
	do_exit=false
	if [[ "$namespace" == "" ]]; then
		do_exit="namespace missing"
	fi

	if [[ "$do_exit" == "false" ]] ; then
		echo "Args valid: Commencing KAPTURE!"
	else
		echo "Found an error in arguments: $do_exit"
		exit 1
	fi
}

exit_if_bad

function tear_down() {
	# Attempt to wipe everything out, even the stuff not being used.  Drop the error like we just don't care.
	kubectl delete -f $BASEDIR/../kube-config -n $namespace --ignore-not-found

	kubectl delete configmaps kapture-config -n $namespace --ignore-not-found

	exit 0
}

function deploy_elastic_search() {
	kubectl scale Deployment es-master -n $namespace --replicas 1
	kubectl scale Deployment es-client -n $namespace --replicas 1
	kubectl scale StatefulSet es-data -n $namespace --replicas 1
	kubectl scale StatefulSet logstash -n $namespace --replicas 1
}

function deploy_prometheus() {
	kubectl create -f $BASEDIR/../kube-config/prometheus.yml -n $namespace
}

function deploy_redis() {
	# The logic here is somewhat convoluted because of how Redis clusters behave.  A cluster must start with one (and only one)
	# master.  In order to do this, we bootstrap a master and then add the slaves to it once it has started up.  After that, we
	# destroy the master so that we have a Redis cluster managed and replicated by Kubernetes.
	kubectl create -f $BASEDIR/../kube-config/redis-master.yml -n $namespace

	echo "Waiting for Redis master to start..."
	role=$(kubectl exec redis-master -n $namespace -c sentinel -- bash -c "redis-cli -p 26379 sentinel master mymaster | grep ^role-reported -A 1" 2> /dev/null)
	until echo $role | grep -m 1 "master" ; do
		sleep 2
		role=$(kubectl exec redis-master -n $namespace -c sentinel -- bash -c "redis-cli -p 26379 sentinel master mymaster | grep ^role-reported -A 1" 2> /dev/null)
	done

	kubectl scale rc redis -n $namespace --replicas $redis_count
	kubectl scale rc redis-sentinel -n $namespace --replicas 3

	echo "Waiting for Redis slaves to register with the master (this may take some time)..."
	slaves=$(kubectl exec redis-master -n $namespace -c master -- bash -c "redis-cli info | grep ^connected_slaves" 2> /dev/null)
	until echo $slaves | grep -m 1 "connected_slaves:[^0]" ; do
		sleep 2
		# kubectl gives an error when the container isn't ready that really doesn't matter, so it just gets dropped on the floor.
		slaves=$(kubectl exec redis-master -n $namespace -c master -- bash -c "redis-cli info | grep ^connected_slaves" 2> /dev/null)
	done

	echo "Removing Redis master..."
	kubectl delete -f $BASEDIR/../kube-config/redis-master.yml -n $namespace
	kubectl scale Deployment rkconn -n $namespace --replicas 1
}

if [ "on" = $delete ] ; then
	tear_down
else
	kubectl create ns $namespace
	kubectl create configmap -n $namespace kapture-config \
		--from-literal=STORE_COUNT="$stores" \
		--from-literal=CUSTOMERS="$customers" \
		--from-literal=SIMULATION="$simulation_time"

	kubectl apply -k $BASEDIR/.. -n $namespace

	echo "Waiting for at least one kafka instance to startup..."
	until kubectl exec kafka-0 -- opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server=localhost:9093 > /dev/null 2>&1
	do
		sleep 2
	done

	if [ "on" = $deploy_prometheus ]; then
		echo "Deploying prometheus connectors..."
		deploy_prometheus
	fi

	if [ "on" = $deploy_redis ]; then
		echo "Deploying Redis..."
		deploy_redis
	fi

	if [ "on" = $deploy_elastic_search ]; then
		echo "Deploying elasticsearch and logstash..."
		deploy_elastic_search
	fi

	echo "Scaling load generators now to $load_generators..."

	kubectl scale Deployment data-loader -n $namespace --replicas $load_generators

	echo "Done scaling !"
fi
