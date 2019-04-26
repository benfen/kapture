from determinator import distance_to_line, simple_linear_regression
from os import listdir, path
from sys import argv

def parse_data_point(data):
    parts = data.split("|")
    return (float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5]), float(parts[7]))

def load_result_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        cpu = []
        memory = []
        network = []
        disk = []
        messages = []

        for i in range(2, len(lines)):
            parts = parse_data_point(lines[i])
            cpu.append(float(parts[0]))
            memory.append(float(parts[1]))
            network.append(float(parts[2]))
            disk.append(float(parts[3]))
            messages.append(float(parts[4]))

        return (cpu, memory, network, disk, messages)

class ResultCharacterization:

    def __init__(self, filename):
        parts = path.splitext(path.basename(filename))[0].split("_")

        self.provider = parts[0]
        self.node_type = parts[1]
        self.redis_enabled = len(parts) == 7
        self.limit = int(parts[5])
        self.load_data(filename)

    def compare(self, result):
        cpu, memory, network, disk, messages = result
        last_messages = 0

        sum = 0
        for x in range(0, len(cpu)):
            # Some of the data captured is post-decline in Kapture.  Since we're using a simpel linear model,
            # that could mess up the comparison.  As such, ignore those values that follow an apparent drop-off.
            if last_messages >= messages[x]:
                break
            last_messages = messages[x]

            sum += distance_to_line(((x + 1), cpu[x]), self.cpu) ** 2
            sum += distance_to_line(((x + 1), memory[x]), self.memory) ** 2
            sum += distance_to_line(((x + 1), network[x]), self.network) ** 2
            sum += distance_to_line(((x + 1), disk[x]), self.disk) ** 2
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
        # Ignore Redis and minikube results for now - can be added later
        if c.provider == "minikube" or c.redis_enabled != redis_enabled:
            continue

        scores.append((c.compare(results), c))

    scores.sort(key = lambda val: val[0])
    print("{0:<10}{1:<10}{2:<20}".format("Score", "Provider", "Node Type"))
    for score in scores:
        print("{0:<10.2f}{1:<10}{2:<20}".format(score[0], score[1].provider, score[1].node_type))

if __name__ == "__main__": 
    main()