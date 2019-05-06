#!/bin/bash

set -e

function python_version() {
    $1 -c 'import sys; print(sys.version_info[0])'
}

echo $python_command

if [[ ! -z "$python_command" && "3" == "$(python_version $python_command)" ]]; then
    # Do something so the conditional can exist
    echo "" > /dev/null
elif [[ ! -z "$(command -v python3)" && "3" == "$(python_version python3)" ]]; then
    python_command=python3
elif [[ ! -z $(command -v python) && "3" == "$(python_version python)" ]]; then
    python_command=python
elif [[ ! -z $(command -v py) && "3" == "$(python_version py)" ]]; then
    python_command=py
else
    echo "Unable to locate python3 on this machine.  Please install python3 or provide a path to a python3 installation on your machine to use the benchmark tool."
    exit 1
fi

flags=

if [ "on" == "$redis" ]; then
	flags="$flags -r"
fi

if [ "on" == "$characterize" ]; then
	flags="$flags --characterize"
fi

$python_command benchmark.py $max_generators $flags --heartbeat $heartbeat
