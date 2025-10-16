CC = gcc
CFLAGS = -Wall -pthread

OUT = zintest

all: $(OUT)

zintest: main.o pixel.o
	   $(CC) $(CFLAGS) main.o pixel.o -o zintest


main.o: main.c pixel.c
	   $(CC) $(CFLAGS) -c main.c

pixel.o: pixel.c pixel.h
	   $(CC) $(CFLAGS) -c pixel.c

clean:
	   rm -f *.o
