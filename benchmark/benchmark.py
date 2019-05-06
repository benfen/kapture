import characterization
from urllib.parse import quote
from urllib.request import urlopen
from zipfile import ZipFile
from time import sleep
import argparse
import io
import requests
import shutil
import os
import subprocess
import json

def configure_prometheus(namespace):
    """Configures a cluster to use Prometheus.

    Fetches the prometheus-recipes repo and runs the script from there to configure the cluster to use it.

    Args:
        namespace: Comma-separated list of namespaces for Prometheus to watch
    """

    shutil.rmtree('./temp', ignore_errors=True)
    result = requests.get('https://codeload.github.com/carbonrelay/prometheus-recipes/zip/master')  

    zip = ZipFile(io.BytesIO(result.content))
    zip.extractall('.')

    os.rename('prometheus-recipes-master', 'temp')

    # ZipFile's extractall method messes up files permissions, so we need to add execute permissions back.
    os.chmod('./temp/prometheus-recipes.sh', 0o755)
    os.chmod('./temp/prometheus.sh', 0o755)

    # Script occasionally fails to deploy one or two things on the first pass.  Do it twice.
    subprocess.check_output(['./temp/prometheus-recipes.sh', namespace, '-npk'])
    subprocess.check_output(['./temp/prometheus-recipes.sh', namespace, '-npk'])

def top_nodes():
    """Retrieves current memory/cpu usage of nodes.

    Fetches current usage of ndoes in the cluster.  Retrieves values as percentages and then averages those percents
    against the current number of nodes in the cluster.

    Returns:
        A tuple (cpu usage, memory usage) representing current usage by the nodes.
    """

    node_lines = subprocess.check_output(['kubectl', 'top', 'nodes', '--no-headers']).split()
    length = len(node_lines)

    cpu = memory = 0
    for index in range(0, length, 5):
        cpu += float(node_lines[index + 2][:-1])
        memory += float(node_lines[index + 4][:-1])

    length /= 5
    return (cpu / length, memory / length)

def prometheus_query(query):
    """Performs a query against prometheus.

    Utilizes kubectl to execute a command within the prometheus container.  Assumes that the query given
    only returns one value and only returns that value.

    Args:
        query - Prometheus QL query to make.  Should only fetch one value.

    Returns:
        A single float representing the result of the provided query.
    """
    query_url = 'http://localhost:9090/api/v1/query?query=' + quote(query, safe='~@#$&()*!+=:;,.?/\'')
    response = subprocess.check_output(['kubectl', 'exec', 'prometheus-k8s-0', '-n', 'monitoring', '-c', 'prometheus',
        '--', 'wget', '-O', '-', '-q', query_url])

    parsed_response = json.loads(response)

    return float(parsed_response['data']['result'][0]['value'][1])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('generators', type=int, default=-1, nargs='?',
                    help='The maximum number of generators to run as part of this test.  ' +
                        'If the number is less than 1, it will run until it observes a decrease in the message throughput in Kafka')
    parser.add_argument('-r', '--redis', action='store_true',
                    help='Include Redis in Kapture as part of the test')
    parser.add_argument('--characterize', action='store_true',
                    help='Attempts to characterize the performance of the cluster based on previously collected data.  ' +
                        'Will run at the end after the benchmark.')
    args = parser.parse_args()

    max_generators = int(args.generators)
    characterize = args.characterize
    namespace = 'test'

    configure_prometheus(namespace)

    os.chdir('..')
    with open('./benchmark/temp/results.json', 'w') as results:
        result_data = {
            'configuration': {
                'redis': args.redis
            },
            'data': []
        }

        flags = '-p'
        if args.redis:
            flags = flags + 'r'

        subprocess.check_output(['./kapture.sh', namespace, '1', flags])
        sleep(1 * 60)

        last_message_rate = 0
        messages_declining = False
        generators = 1
        while (max_generators <= 0 and not messages_declining) or generators <= max_generators:
            sleep(4.5 * 60)

            cpu, memory = top_nodes()
            network = prometheus_query('sum(rate(node_network_receive_bytes_total[3m]))')
            disk = prometheus_query('sum(rate(node_disk_written_bytes_total[3m]))')

            messages1m = prometheus_query('sum(rate(bps_messages_produced[1m]))')
            messages2m = prometheus_query('sum(rate(bps_messages_produced[2m]))')
            messages3m = prometheus_query('sum(rate(bps_messages_produced[3m]))')

            data = {
                'generators': generators,
                'cpu': cpu,
                'memory': memory,
                'network': network,
                'disk': disk,
                'messages1m': messages1m,
                'messages2m': messages2m,
                'messages3m': messages3m
            }

            print(json.dumps(data))
            result_data['data'].append(data)

            if messages_declining or last_message_rate > messages2m:
                messages_declining = True
            else:
                last_message_rate = messages2m

            generators += 1
            subprocess.check_output(['kubectl', 'scale', 'Deployment', 'data-loader', '-n', namespace, '--replicas', str(generators)])

        results.write(json.dumps(result_data))

    if characterize:
        characterization.characterize_data(result_data)

    print('Removing created Kapture resources from the cluster...')
    subprocess.check_output(['./kapture.sh', namespace, '--delete'])
    print('Removing created Prometheus resources from the cluster...')
    os.chdir('benchmark/temp')
    print('Cleaning up created testing namespace...')
    subprocess.check_output(['./prometheus-recipes.sh', namespace, '--delete'])

if __name__ == '__main__': 
    main()