CC = gcc
CFLAGS = -Wall -pthread -lm

OUT = zintest

all: $(OUT)

zintest: main.o
	   $(CC) $(CFLAGS) main.o -o zintest

main.o: main.c pixel.c
	   $(CC) $(CFLAGS) -c main.c

clean:
	   rm -f *.o
