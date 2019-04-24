#!/bin/bash

# m4_ignore(
echo "This is just a script template, not the script (yet) - pass it to 'argbash' to fix this." >&2
exit 11  #)Created by argbash-init v2.8.0
# Rearrange the order of options below according to what you would like to see in the help message.
# ARG_OPTIONAL_SINGLE([mode], [m], [Mode to run the benchmark in (fast, normal, slow).  Slower tests will give more accurate values and a wider range of them], [normal])
# ARG_OPTIONAL_BOOLEAN([redis], [r], [Include Redis in Kapture as part of the test], [off])
# ARG_POSITIONAL_SINGLE([max-generators],[The maximum number of generators to run as part of this test.  If the number is less than 1, it will run forever],[-1])
# ARG_HELP([Performs a benchmark of Kapture against a cluster])
# ARGBASH_GO

# [ <-- needed because of Argbash

printf "'%s' is %s\\n" 'mode' "$_arg_mode"
printf "'%s' is %s\\n" 'redis' "$_arg_redis"
printf "Value of '%s': %s\\n" 'max-generators' "$_arg_max_generators"

# ] <-- needed because of Argbash

export mode=$_arg_mode
export redis=$_arg_redis
export max_generators=$_arg_max_generators

BASEDIR=$(dirname $0)

(
    cd $BASEDIR/benchmark
    ./benchmark.sh
)
