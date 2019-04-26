from determinator import distance_to_line, simple_linear_regression
from os import listdir, path
from sys import argv

def parse_data_point(data):
    """Parse a single data point

    Args:
        data: A single line (in the form of a string) from a results file

    Returns:
        A tuple in the form (cpu, memory, network, disk, messages), where each element of the tuple
        represents a single value from that line.
    """
    parts = data.split("|")
    return (float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5]), float(parts[7]))

def load_result_file(filename):
    """Loads data from a result file

    Args:
        filename: Name of the file to load the data from

    Returns:
        A tuple if the form (cpu, memory, network, disk, messages), where each element of the tuple
        represents an array of the corresponding elements in the results file.
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        cpu = []
        memory = []
        network = []
        disk = []
        messages = []

        last_messages = 0

        for i in range(2, len(lines)):
            parts = parse_data_point(lines[i])

            # Some of the data captured is post-decline in Kapture.  Since we're using a simpel linear model,
            # that could mess up the comparison.  As such, ignore those values that follow an apparent drop-off.
            current_messages = float(parts[4])
            if last_messages > current_messages:
                break
            last_messages = current_messages

            cpu.append(float(parts[0]))
            memory.append(float(parts[1]))
            network.append(float(parts[2]))
            disk.append(float(parts[3]))
            messages.append(current_messages)

        return (cpu, memory, network, disk, messages)

class ResultCharacterization:
    """Data container for performance characterizing metrics from a Kapture result

    This has a couple of methods for generating data from a file and comparing it to other data.

    Attributes:
        provider: A string naming the provider used by this characterization
        node_type: A string naming the type of node used by this characterization
        redis_enabled: Boolean indicating whether Redis is enabled
        limit: Number of result rows from the characterization to use to build the regression
        cpu: A tuple (a, b) meant to represent a simple linear regression over cpu
        memory: A tuple (a, b) meant to represent a simple linear regression over memory
        network: A tuple (a, b) meant to represent a simple linear regression over network
        disk: A tuple (a, b) meant to represent a simple linear regression over disk
        messages: A tuple (a, b) meant to represent a simple linear regression over messages
    """

    def __init__(self, filename):
        parts = path.splitext(path.basename(filename))[0].split("_")

        self.provider = parts[0]
        self.node_type = parts[1]
        self.redis_enabled = len(parts) == 7
        self.limit = int(parts[5])
        self.load_data(filename)

    def compare(self, result):
        cpu, memory, network, disk, messages = result

        sum = 0
        for x in range(0, len(cpu)):
            sum += distance_to_line(((x + 1), cpu[x]), self.cpu) ** 2
            sum += distance_to_line(((x + 1), memory[x]), self.memory) ** 2
            # Quick patch.  Network and disk are much larger values and seem to contribute much more.
            sum += distance_to_line(((x + 1), network[x]), self.network) ** 2 / 10
            sum += distance_to_line(((x + 1), disk[x]), self.disk) ** 2 / 10
            sum += distance_to_line(((x + 1), messages[x]), self.messages) ** 2

        return sum

    def load_data(self, filename):
        (cpu, memory, network, disk, messages) = load_result_file(filename)
        points = list(range(1, self.limit + 1))

        self.cpu = simple_linear_regression(points, cpu)
        self.memory = simple_linear_regression(points, memory)
        self.network = simple_linear_regression(points, network)
        self.disk = simple_linear_regression(points, disk)
        self.messages = simple_linear_regression(points, messages)

def main():
    results_dir = path.join(path.dirname(path.realpath(__file__)), "results")
    characterizations = [ ResultCharacterization(path.join(results_dir, filename)) for filename in listdir(results_dir) ]

    test_file = path.abspath(argv[1])
    redis_enabled = len(argv) > 2 and argv[2].lower() == 'true'
    results = load_result_file(test_file)
    scores = []

    for c in characterizations:
        # Ignore minikube results for now - can be added later
        if c.provider == "minikube" or c.redis_enabled != redis_enabled:
            continue

        scores.append((c.compare(results), c))

    scores.sort(key = lambda val: val[0])
    print("{0:<10}{1:<10}{2:<20}".format("Score", "Provider", "Node Type"))
    for score in scores:
        print("{0:<10.2f}{1:<10}{2:<20}".format(score[0], score[1].provider, score[1].node_type))

if __name__ == "__main__": 
    main()