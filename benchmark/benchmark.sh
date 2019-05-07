#!/bin/bash

set -e

if [[ ! -z "$python_command" ]]; then
    # Do something so the conditional can exist
    echo "" > /dev/null
elif [[ ! -z "$(command -v python3)" ]]; then
    python_command=python3
elif [[ ! -z $(command -v python) ]]; then
    python_command=python
elif [[ ! -z $(command -v py) ]]; then
    python_command=py
else
    echo "Unable to locate python on this machine.  Please install python or provide a path to a python installation on your machine to use the benchmark tool."
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
