# This is a sample of a execution script
# It must accept 3 parameters:
# 	* Host (first argument: $1)
#	* Position (second argument: $2)
# 	* Robot name (third argument: $3)

# Usage: ./execute.sh localhost 3 myrobot

cd sample_code;
java jClient -host $1 -pos $2 -robname $3