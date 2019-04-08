#!/bin/bash

# m4_ignore(
echo "This is just a script template, not the script (yet) - pass it to 'argbash' to fix this." >&2
exit 11  #)Created by argbash-init v2.8.0
# Rearrange the order of options below according to what you would like to see in the help message.
# ARG_OPTIONAL_SINGLE([stores],[s],[Number of stores to initialize the BigPetStore with.  Will correspond to the number of Kafka topcis that will be generated],[13])
# ARG_OPTIONAL_SINGLE([customers],[c],[Number of customers to simulate for BigPetStore],[500000])
# ARG_OPTIONAL_SINGLE([simulation],[d],[Time (in days) to run the BigPetStore simulation over],[15000]))
# ARG_OPTIONAL_BOOLEAN([delete], [], [Deletes all the kubernetes resources generated by a normal run], [off])
# ARG_POSITIONAL_SINGLE([namespace],[The namespace to deploy Kapture to],[])
# ARG_DEFAULTS_POS
# ARG_HELP([<The general help message of my script>])
# ARGBASH_GO

# [ <-- needed because of Argbash

printf 'Value of --%s: %s\n' 'stores' "$_arg_stores"
printf 'Value of --%s: %s\n' 'cusomters' "$_arg_cusomters"
printf 'Value of --%s: %s\n' 'simulation' "$_arg_simulation"
printf "'%s' is %s\\n" 'delete' "$_arg_delete"
printf "Value of '%s': %s\\n" 'namespace' "$_arg_namespace"

# ] <-- needed because of Argbash

export namespace=$_arg_namespace
export customers=$_arg_customers
export simulation_time=$_arg_simulation
export stores=$_arg_stores

./scripts/kapture.sh $_arg_delete
