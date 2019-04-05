echo "total transactions: $total_transactions"
echo "namespace: $namespace"

function exit_if_bad() {
	do_exit=false
	if [[ "$namespace" == "" ]]; then
		do_exit="namespace missing"
	fi
	if [[ "$total_transactions" == "" ]]; then
		do_exit="transactions missing"
	fi

	if [[ "$do_exit" == "false" ]] ; then
		echo "Args valid: Commencing KAPTURE!"
	else
		echo "Found an error in arguments: $do_exit"
		exit 1
	fi
}

exit_if_bad

kubectl create ns $namespace
kubectl create -f zk.yml  -n $namespace
kubectl create -f kafka.yml -n $namespace
kubectl create -f redis.yml -n $namespace
kubectl create -f rk-conn.yml -n $namespace
