import json

def main():
    with open('temp/results.json') as r, open('results/catalog.json') as c:
        results = json.load(r)
        catalog = json.load(c)

        kube_provider = subprocess.check_output(['kubectl', 'get', 'nodes', '-o',
            'jsonpath={.items[*].metadata.labels.kubernetes\.io/hostname}'])

        if 'gke' in kube_provider:
            provider = 'gke'
        else:
            provider = 'minikube'

        if provider == 'minikube':
            nodes = {
                "minikube": 1
            }
        else:
            nodes = {}
            node_configuration = subprocess.check_output(['kubectl', 'get', 'nodes', '-o',
                'jsonpath={.items[*].metadata.labels.beta\.kubernetes\.io/instance-type}'])

            for node in node_configuration.split():
                if node in nodes:
                    nodes[node] += 1
                else:
                    nodes[node] = 1

if __name__ == '__main__': 
    main()