##########################################################################################################
##																										##
##	Usage:																								##
##		./run_comp.sh <options>																			##
##	Options:																							##
##		-c <language> <script_file>					will compile the source code with a given script 	##
##													filename may be provided or not, if not provided	##
##													it will consider "myrob"							##
##																										##
##		-r <language> [filename]					It will run the executable based on a language		##
##																										##
##	Languages supported:																				##
##		C/C++ (c/cpp)																					##
##		Java (java)																						##
##		Python (python)																					##
##																										##
##########################################################################################################

function usage {
	printf "Usage: ./run_comp.sh <options>\n"
	printf "Options:\n"
	printf "\t-c <script_file>\t\tCompile the source code with a given script\n"
	printf "\t-r <language>\t\tExecute the binary file with default name: myrob)\n"
	printf "\t-h\t\t\t\tDisplay this message\n"
	printf "\nLanguages supported: \n"
	printf "\tC/C++ (c/cpp)\n"
	printf "\tJava (java)\n"
	printf "\tPython (python)\n"
}
compile=false
run=false

while getopts ":c::r::h" opt; do
  	case "${opt}" in
	    c)
			if [ "$compile" = true ]; then
				echo "Not allowed to use -c option more than one time in same script."
				exit 1
			fi
			compile=true
           	script=$OPTARG
	      	;;
	    r)
			if [ "$run" = true ]; then
				echo "Not allowed to use -r option more than one time in same script."
				exit 1
			fi
			run=true
			language=$OPTARG
			;;
		h)
			usage
			exit 1
			;;
	    \?)
		    echo "Invalid option: -$OPTARG" >&2
		    exit 1
		    ;;
	    :)
	      	echo "Option -$OPTARG requires an argument." >&2
	      	exit 1
	      	;;
  	esac
done
shift $((OPTIND -1))

if [ "$compile" = false ] && [ "$run" = false ];
then
	usage
	exit 1
fi

if [ "$compile" = true ];
then
	echo "Executing script to compile"
	./$script
fi

if [ "$run" = true ];
then
	case "$language" in
		"java") 
			echo "Executing a Java agent"
			java -jar myrob.jar
			;;
		"cpp"|"c")
			echo "Executing a C/C++ agent"
			./myrob
			;;
		"python")
			echo "Executing a python agent"
			python myrob.py
			;;
		*)
			echo "Language not supported"
			;;
	esac
fi