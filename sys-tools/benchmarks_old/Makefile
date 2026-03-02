CC = gcc
CFLAGS = -Wall -pthread

OUT = zintest

all: $(OUT)

zintest: main.o
	   $(CC) $(CFLAGS) main.o -o zintest -lm

main.o: main.c pixel.c
	   $(CC) $(CFLAGS) -c main.c

clean:
	   rm -f *.o
