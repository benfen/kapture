import determinator
import json
import os
from sys import argv
from os.path import join

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
        node_configuration: A string naming the type of node used by this characterization
        redis_enabled: Boolean indicating whether Redis is enabled

        generators: Part of the six data lists.  Indicates number of generators for a given data point.
        cpu: Part of the six data lists.  Indicates usage of cpu for a given data point.
        memory: Part of the six data lists.  Indicates usage of memory for a given data point.
        network: Part of the six data lists.  Indicates network usage for a given data point.
        disk: Part of the six data lists.  Indicates disk usage for a given data point.
        messages: Part of the six data lists.  Indicates number of messages for a given data point.

        cpu_regression: A tuple (a, b) meant to represent a simple linear regression over cpu
        memory_regression: A tuple (a, b) meant to represent a simple linear regression over memory
        network_regression: A tuple (a, b) meant to represent a simple linear regression over network
        disk_regression: A tuple (a, b) meant to represent a simple linear regression over disk
        messages_regression: A tuple (a, b) meant to represent a simple linear regression over messages
    """

    def __init__(self, provider, node_configuration, configuration):
        """Initializes this characterization.

        Sets up the characterization.  Note that the regressions defined on the class are not defined until
        `create_regression` is explicitly called.

        Args:
            provider - String; provider for this cluster (e.g. minikube, gke)
            node_configuration - String; configurations of nodes being used in the cluster (e.g. 2_n1-standard-8)
            configuration - String; list of configuration flags.  The string 'r' would represent having Redis enabled.
                By convention, the string '-' represents the default configuration.
        """
        self.provider = provider
        self.node_configuration = node_configuration
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
        """Add a single set of results to the data in this characterization.  All data is added to this instance.

        Args:
            results - Dict representation of the JSON from a benchmark run
        """
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
            result: Dict representation of the JSON from a benchmark run
        
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
    """Characterizes the data provided based on known results.

    Outputs results to standard out.

    Args:
        data: Dict representation of the JSON from a benchmark run to be characterized
    """
    characterizations = load_data()

    scores = []
    for c in [ ch for ch in characterizations if ch.redis_enabled == data['configuration']['redis'] ]:
        scores.append((c.compare(data), c))

    scores.sort(key = lambda val: val[0])
    print('{0:<10}{1:<10}{2:<20}'.format('Score', 'Provider', 'Node Configuration'))
    for score in scores:
        print('{0:<10.2f}{1:<10}{2:<20}'.format(score[0], score[1].provider, score[1].node_configuration))

def load_data():
    """Loads data for previous runs to compare against

    Returns:
        List of characterizations
    """
    characterizations = []
    basedir = join(os.path.dirname(__file__), 'results')
    result_dirs = os.listdir(basedir)
    providers = []
    for item in result_dirs:
        if not item == 'minikube' and os.path.isdir(join(basedir, item)):
            providers.append(item)

    for provider in providers:
        provider_dir = join(basedir, provider)
        for node_configuration in os.listdir(provider_dir):
            node_configurations = {}

            config_dir = join(provider_dir, node_configuration)
            for data in os.listdir(config_dir):
                name_parts = os.path.splitext(data)[0].split('-')

                if len(name_parts) == 2:
                    key = name_parts[1]
                else:
                    key = '-'

                if not key in node_configurations:
                    characterization = ResultCharacterization(provider, node_configuration, key)
                    node_configurations[key] = characterization
                else:
                    characterization = node_configurations[key]

                characterization.add_data(join(config_dir, data))

            characterizations.extend(node_configurations.values())

    return characterizations

def main():
    with open(os.path.abspath(argv[1])) as f:
        characterize_data(json.load(f))

if __name__ == '__main__': 
    main()