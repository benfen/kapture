import shutil
import json
import subprocess

def get_node_statistics():
    node_data = json.loads(subprocess.check_output(['kubectl', 'get', 'nodes', '-o', 'json']))

    if 'gke' in node_data['items'][0]['metadata']['name']:
        provider = 'gke'
    else:
        provider = 'minikube'

    if provider == 'minikube':
        cpu = node_data['items']['status']['capacity']['cpu']
        memory = round(int(node_data['items']['status']['capacity']['memory'].rstrip('Ki')) / 1024**2, 2)
        nodes = {
            'minikube': 1
        }
    else:
        cpu = 0
        memory = 0
        nodes = {}

        for node in node_data['items']:
            cpu += int(node['status']['capacity']['cpu'])
            memory += int(node['status']['capacity']['memory'].rstrip('Ki'))
            label = node['metadata']['labels']['beta.kubernetes.io/instance-type']
            if label in nodes:
                nodes[label] += 1
            else:
                nodes[label] = 1

        memory = round(memory / 1024**2, 2)

    return (provider, nodes, cpu, memory)

def get_config_identifier(nodes):
    name = ''
    for node in sorted(nodes.keys()):
        name += '{}_{}_'.format(nodes[node], node)

    return name.rstrip('_')

def append_to_catalog(result_path, catalog_path):
    with open(result_path) as r, open(catalog_path) as c:
        catalog = json.load(c)
        results = json.load(r)

    old_messages = 0
    summary = 0
    max = 0
    for counter, item in enumerate(results['data']):
        if item['messages'] > old_messages:
            summary += item['messages']
            old_messages = item['messages']
            max = counter + 1

    summary /= (max * (max + 1) / 2)
    node_stats = get_node_statistics()

    for provider in catalog:
        # Currently do not support adding extra providers automatically
        if node_stats[0] == provider['provider']:
            item = None
            runs = 0
            for config in provider['data']:
                if config['nodes'] == node_stats[1] and config['configuration'] == results['configuration']:
                    item = config
                    runs = len(item['runs'])
                    break

            flag_string = "-"
            if results['configuration']['redis']:
                flag_string += "r"
            flag_string.rstrip("-")

            run = {
                'path': '{}/{}/{}{}.json'.format(node_stats[0], get_config_identifier(node_stats[1]), runs, flag_string),
                'max': max,
                'summary': summary
            }

            if item is not None:
                item['summary'] = (item['summary'] * runs + summary) / (runs + 1)
                item['runs'].append(run)
            else:
                item = {
                    'nodes': node_stats[1],
                    'configuration': results['configuration'],
                    'cpus': node_stats[2],
                    'memory': node_stats[3],
                    'summary': summary,
                    'runs': [run]
                }
                provider['data'].append(item)

            shutil.copyfile(result_path, '{}/{}'.format('results', run['path']))
            with open(catalog_path, 'w') as c:
                json.dump(catalog, c, sort_keys=True, indent=4)
