#!/bin/bash

# m4_ignore(
echo "This is just a script template, not the script (yet) - pass it to 'argbash' to fix this." >&2
exit 11  #)Created by argbash-init v2.8.0
# Rearrange the order of options below according to what you would like to see in the help message.
# ARG_OPTIONAL_SINGLE([heartbeat], [], [Configures a heartbeat for Kapture to use while waiting for the benchmark.  The heartbeat specifies the time in seconds for Kapture to wait before pinging the server to get cpu memory statistics.  These stats are then stored in the updates.json file next to results.json.  If the value for the heartbeat is less than or equal to 0, the heartbeat will not trigger; this is the default behavior], [-1])
# ARG_OPTIONAL_SINGLE([python-command], [], [As long as a version of python3 is installed on the path, this should not be needed.  Absolute path to the binary for python3.], [])
# ARG_OPTIONAL_BOOLEAN([redis], [r], [Include Redis in Kapture as part of the test], [off])
# ARG_OPTIONAL_BOOLEAN([characterize], [], [Attempts to characterize the performance of the cluster based on previously collected data.  Will run at the end after the benchmark.  Requires python to be installed on the system.], [off])
# ARG_POSITIONAL_SINGLE([max-generators],[The maximum number of generators to run as part of this test.  If the number is less than 1, it will run until it observes a decrease in the message throughput in Kafka],[-1])
# ARG_DEFAULTS_POS
# ARG_HELP([Performs a benchmark of Kapture against a cluster])
# ARGBASH_GO

# [ <-- needed because of Argbash

printf "Value of '%s': %s\\n" 'heartbeat' "$_arg_heartbeat"
printf "Value of '%s': %s\\n" 'python-command' "$_arg_python_command"
printf "'%s' is %s\\n" 'characterize' "$_arg_characterize"
printf "'%s' is %s\\n" 'redis' "$_arg_redis"
printf "Value of '%s': %s\\n" 'max-generators' "$_arg_max_generators"

# ] <-- needed because of Argbash

export heartbeat=$_arg_heartbeat
export python_command=$_arg_python_command
export redis=$_arg_redis
export max_generators=$_arg_max_generators
export characterize=$_arg_characterize

BASEDIR=$(dirname $0)

(
    cd $BASEDIR/benchmark
    ./benchmark.sh
)
