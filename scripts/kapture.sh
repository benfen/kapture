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
	kubectl delete -f prometheus.yml -n $namespace
	kubectl delete -f load-gen.yml -n $namespace
	kubectl delete -f rk-conn.yml -n $namespace
	kubectl delete -f redis.yml -n $namespace
	kubectl delete -f redis-master.yml -n $namespace
	kubectl delete -f kafka.yml -n $namespace
	kubectl delete -f zk.yml -n $namespace

	kubectl delete configmaps kapture-config -n $namespace

	exit 0
}

# Temporary hack for testing
if [ "on" = $delete ]; then
	tear_down
fi

kubectl create ns $namespace
kubectl create configmap -n $namespace kapture-config --from-literal=STORE_COUNT="$stores" \
	--from-literal=CUSTOMERS="$customers" --from-literal=SIMULATION="$simulation_time"
kubectl create -f redis-master.yml -n $namespace
kubectl create -f zk.yml  -n $namespace
kubectl create -f kafka.yml -n $namespace
kubectl create -f rk-conn.yml -n $namespace

if [ "on" = $deploy_prometheus ]; then  
	kubectl create -f prometheus.yml -n $namespace
fi

echo "Waiting for Redis master to start..."
role=$(kubectl exec redis-master -c master -- bash -c "redis-cli info | grep ^role")
until echo $role | grep -m 1 "role:master" ; do
	role=$(kubectl exec redis-master -c master -- bash -c "redis-cli info 2> /dev/null | grep ^role") ; sleep 2
done

kubectl create -f redis.yml -n $namespace

echo "Waiting for Redis slaves to start..."
slaves=$(kubectl exec redis-master -c master -- bash -c "redis-cli info | grep ^connected_slaves")
until echo $slaves | grep -m 1 "connected_slaves:2" ; do
	# kubectl gives an error when the container isn't ready that really doesn't matter, so it just gets dropped on the floor.
	slaves=$(kubectl exec redis-master -c master -- bash -c "redis-cli info 2> /dev/null | grep ^connected_slaves") ; sleep 2
done

kubectl delete -f redis-master.yml -n $namespace
