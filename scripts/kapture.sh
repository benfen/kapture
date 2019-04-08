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

function tear_down() {
	kubectl delete -f load-gen.yml -n $namespace
	kubectl delete -f rk-conn.yml -n $namespace
	kubectl delete -f redis.yml -n $namespace
	kubectl delete -f kafka.yml -n $namespace
	kubectl delete -f zk.yml -n $namespace

	kubectl delete configmaps kapture-config -n $namespace

	exit 0
}

# Temporary hack for testing
if ! [ -z $1 ]; then
	tear_down
fi

exit_if_bad

kubectl create ns $namespace
kubectl create configmap kapture-config --from-literal=STORE_COUNT="$stores" \
	--from-literal=CUSTOMERS="$customers" --from-literal=SIMULATION="$simulation_time"
kubectl create -f zk.yml  -n $namespace
kubectl create -f kafka.yml -n $namespace
kubectl create -f redis.yml -n $namespace
kubectl create -f rk-conn.yml -n $namespace
