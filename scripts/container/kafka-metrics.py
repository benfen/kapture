from prometheus_client import start_http_server, Counter
import subprocess
import time

# Create a metric to track bps messages
bps_messages = Counter(
    "bps_messages", "Total number of Big Pet store messages received by Kafka", ["id"]
)

if __name__ == "__main__":
    # Start up the server to expose the metrics.
    start_http_server(8000)
    values = {}

while True:
    output = subprocess.check_output(
        [
            "/opt/kafka/bin/kafka-run-class.sh",
            "kafka.tools.GetOffsetShell",
            "--broker-list",
            "kafka-svc:9093",
            "--topic",
            "bps-data",
            "--time",
            "-1",
        ]
    ).decode("utf-8")

    for item in output.split():
        parts = item.split(":")
        past = values.get(parts[1], 0)

        current_value = int(parts[2])
        diff = current_value - past

        bps_messages.labels(id=parts[1]).inc(diff)
        values[parts[1]] = current_value
    time.sleep(5)
