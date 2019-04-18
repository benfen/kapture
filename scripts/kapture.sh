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
	# Attempt to wipe everything out, even the stuff not being used
	kubectl delete -f $BASEDIR/../kube-config -n $namespace

	kubectl delete configmaps kapture-config -n $namespace

	exit 0
}

function deploy_prometheus() {
	kubectl create -f $BASEDIR/../kube-config/prometheus.yml -n $namespace
}

function deploy_redis() {
	kubectl create -f $BASEDIR/../kube-config/redis-master.yml -n $namespace

	echo "Waiting for Redis master to start..."
	role=$(kubectl exec redis-master -n $namespace -c sentinel -- bash -c "redis-cli -p 26379 sentinel master mymaster | grep ^role-reported -A 1")
	until echo $role | grep -m 1 "master" ; do
		sleep 2
		role=$(kubectl exec redis-master -n $namespace -c sentinel -- bash -c "redis-cli -p 26379 sentinel master mymaster | grep ^role-reported -A 1")
	done

	kubectl scale rc redis -n $namespace --replicas $redis_count
	kubectl scale rc redis-sentinel -n $namespace --replicas 3

	echo "Waiting for Redis slaves to register with the master (this may take some time)..."
	slaves=$(kubectl exec redis-master -n $namespace -c master -- bash -c "redis-cli info | grep ^connected_slaves")
	until echo $slaves | grep -m 1 "connected_slaves:[^0]" ; do
		sleep 2
		# kubectl gives an error when the container isn't ready that really doesn't matter, so it just gets dropped on the floor.
		slaves=$(kubectl exec redis-master -n $namespace -c master -- bash -c "redis-cli info | grep ^connected_slaves")
	done

	echo "Removing Redis master..."
	kubectl delete -f $BASEDIR/../kube-config/redis-master.yml -n $namespace
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

	if [ "on" = $deploy_prometheus ]; then
		deploy_prometheus
	fi

	if [ "on" = $deploy_redis ]; then
		deploy_redis
	fi

	kubectl scale Deployment data-loader -n $namespace --replicas $load_generators
fi
