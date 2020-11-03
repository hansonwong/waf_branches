
all: redisrpc.o redisrpc_test.o
	gcc -g -o redisrpc redisrpc.o redisrpc_test.o -lpthread -lhiredis -levent -ljansson
	
redisrpc.o: redisrpc.c
	gcc -g -c redisrpc.c
	
redisrpc_test.o: redisrpc_test.c
	gcc -g -c redisrpc_test.c
	
clean:
	rm -f *.o
	rm -f redisrpc