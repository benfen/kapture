import determinator
import json
import os
from sys import argv

def load_results(results):
    """Loads data from a results array

    Args:
        results: Array of results to load data from

    Returns:
        A tuple of the form (cpu, memory, network, disk, messages), where each element of the tuple
        represents an array of the corresponding elements in the results.
    """
    cpu = []
    memory = []
    network = []
    disk = []
    messages = []

    last_messages = 0

    for data in results:
            # Some of the data captured is post-decline in Kapture.  Since we're using a simplw linear model,
        # that could mess up the comparison.  As such, ignore those values that follow an apparent drop-off.
        current_messages = float(data['messages2m'])
        if last_messages > current_messages:
            break
        last_messages = current_messages

        cpu.append(float(data['cpu']))
        memory.append(float(data['memory']))
        network.append(float(data['network']))
        disk.append(float(data['disk']))
        messages.append(current_messages)

    return (cpu, memory, network, disk, messages)

class ResultCharacterization:
    """Data container for performance characterizing metrics from a Kapture result

    This has a couple of methods for generating data from a file and comparing it to other data.

    Attributes:
        provider: A string naming the provider used by this characterization
        node_type: A string naming the type of node used by this characterization
        redis_enabled: Boolean indicating whether Redis is enabled
        cpu: A tuple (a, b) meant to represent a simple linear regression over cpu
        memory: A tuple (a, b) meant to represent a simple linear regression over memory
        network: A tuple (a, b) meant to represent a simple linear regression over network
        disk: A tuple (a, b) meant to represent a simple linear regression over disk
        messages: A tuple (a, b) meant to represent a simple linear regression over messages
    """

    def __init__(self, provider, node_type, configuration):
        self.provider = provider
        self.node_type = node_type
        self.redis_enabled = 'r' in configuration

        self.generators = []
        self.cpu = []
        self.memory = []
        self.network = []
        self.disk = []
        self.messages = []

        self.cpu_regression = None
        self.memory_regression = None
        self.network_regression = None
        self.disk_regression = None
        self.messages_regression = None

    def add_data(self, results):
        with open(results) as f:
            data = json.load(f)

            for item in data['data']:
                self.generators.append(item['generators'])
                self.cpu.append(item['cpu'])
                self.memory.append(item['memory'])
                self.network.append(item['network'])
                self.disk.append(item['disk'])
                self.messages.append(item['messages2m'])

    def compare(self, result):
        """Compare the provided result to this characterization.

        Args:
            result: A tuple of the form (cpu, memory, network, disk, messages), where each element of the tuple
            represents an array of the corresponding elements in the results file.
        
        Returns:
            Float representation of the quality of the comparison.  A lower number is a better match.
        """
        if self.cpu_regression is None:
            self.create_regressions()

        sum = 0
        for item in result['data']:
            sum += determinator.distance_to_line((item['generators'], item['cpu']), self.cpu_regression) ** 2
            sum += determinator.distance_to_line((item['generators'], item['memory']), self.memory_regression) ** 2

            # Quick patch.  Network and disk are much larger values and seem to contribute much more.
            sum += determinator.distance_to_line((item['generators'], item['network']), self.network_regression) ** 2 / 10
            sum += determinator.distance_to_line((item['generators'], item['disk']), self.disk_regression) ** 2 / 10

            sum += determinator.distance_to_line((item['generators'], item['messages2m']), self.messages_regression) ** 2

        return sum

    def create_regressions(self):
        """Creates the regressions for cpu, memory, network, disk, and messages and attaches them to the class.

            Note that this will simply overwrite any pre-existing regressions that may have existed 
        """
        self.cpu_regression = determinator.simple_linear_regression(self.generators, self.cpu)
        self.memory_regression = determinator.simple_linear_regression(self.generators, self.memory)
        self.network_regression = determinator.simple_linear_regression(self.generators, self.network)
        self.disk_regression = determinator.simple_linear_regression(self.generators, self.disk)
        self.messages_regression = determinator.simple_linear_regression(self.generators, self.messages)

def characterize_data(data):
    characterizations = load_data()

    scores = []
    for c in [ ch for ch in characterizations if ch.redis_enabled == data['configuration']['redis'] ]:
        scores.append((c.compare(data), c))

    scores.sort(key = lambda val: val[0])
    print('{0:<10}{1:<10}{2:<20}'.format('Score', 'Provider', 'Node Configuration'))
    for score in scores:
        print('{0:<10.2f}{1:<10}{2:<20}'.format(score[0], score[1].provider, score[1].node_type))

def load_data():
    characterizations = []
    result_dirs = os.scandir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results'))
    providers = [ item for item in result_dirs if item.is_dir() and not item.name == 'minikube']

    for provider in providers:
        for node_type in os.scandir(provider.path):
            node_configurations = {}

            for data in os.scandir(node_type.path):
                name_parts = os.path.splitext(data.name)[0].split('-')

                if len(name_parts) == 2:
                    key = name_parts[1]
                else:
                    key = '-'

                if not key in node_configurations:
                    characterization = ResultCharacterization(provider.name, node_type.name, key)
                    node_configurations[key] = characterization
                else:
                    characterization = node_configurations[key]

                characterization.add_data(data.path)

            characterizations.extend(node_configurations.values())

    return characterizations

def main():
    with open(os.path.abspath(argv[1])) as f:
        characterize_data(json.load(f))

if __name__ == '__main__': 
    main()