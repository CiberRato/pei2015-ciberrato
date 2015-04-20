# This is a sample of a preparation script to install all the dependencies and compile
# your code.
# In this case we will use a Makefile to compile everything for us.

echo "Compiling library source code.."
cd sample_code/libRobSock;
qmake RobSock.pro
make
echo "Compiling source code.."
cd ..;
gcc -c -Wall -IlibRobSock -o mainRob.o mainRob.c
gcc -c -Wall -IlibRobSock -o robfunc.o robfunc.c
g++ -o robsample mainRob.o robfunc.o -LlibRobSock -lRobSock
echo "Done."