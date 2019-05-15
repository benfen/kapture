#!/bin/bash

set -e

BASEDIR=$(dirname $0)

(
    cd $BASEDIR/benchmark

    if [[ ! -z "$(command -v python3)" ]]; then
		python_command=python3
	elif [[ ! -z $(command -v python) ]]; then
		python_command=python
	elif [[ ! -z $(command -v py) ]]; then
		python_command=py
	else
		echo "Unable to locate python on this machine.  Please install python or provide a path to a python installation on your machine to use the benchmark tool."
		exit 1
	fi

	$python_command benchmark.py "$@"
)
