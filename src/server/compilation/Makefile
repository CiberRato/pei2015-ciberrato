target = cheesy

# Compilation in c requires to have libRobSock on /usr/lib (at least) and ldconfig it
# Or export that path 
# We have to make this decision (first option is to load libraries on container, not a big deal)

$(target):	*.o $(target).o
	gcc -o $(target) $(shell ls *.o) -lRobSock

%.o: %.c
	gcc -g -c $<

clean:
	rm -rf *.o