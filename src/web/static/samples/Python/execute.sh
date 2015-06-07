# This is a sample of a execution script
# It must accept 3 parameters:
# 	* Host (first argument: $1)
#	* Position (second argument: $2)
# 	* Robot name (third argument: $3)

# Usage: ./execute.sh localhost 3 myrobot

# cd sample_code;
python labi_robot_example.py -host $1 -position $2 -robotname $3
