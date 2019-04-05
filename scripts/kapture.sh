echo "total transactions: $_arg_total_transactions"
echo "namespace: $_arg_namespace"

kubectl create ns $_arg_namespace
kubectl create -f zk.yml  -n $_arg_namespace
kubectl create -f kafka.yml -n $_arg_namespace
kubectl create -f redis.yml -n $_arg_namespace
kubectl create -f rk-conn.yml -n $_arg_namespace
