
all: xmlrpc_dispatch_test.o xmlrpc_dispatch.o
	gcc -g -o xmlrpc_dispatch_test xmlrpc_dispatch_test.o xmlrpc_dispatch.o -lxmlrpc_client -ljansson -lpthread
	

xmlrpc_dispatch_test.o: xmlrpc_dispatch_test.c
	gcc -g -c xmlrpc_dispatch_test.c

xmlrpc_dispatch.o: xmlrpc_dispatch.c
	gcc -g -c xmlrpc_dispatch.c

clean:
	rm -f *.o
	rm -f xmlrpc_dispatch_test
