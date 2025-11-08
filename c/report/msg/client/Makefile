CC = gcc
CFLAGS = -Wall -Wextra -O2 -Ilib

SRC = msg.c lib/socketops.c

TARGET = program

all: $(TARGET)

$(TARGET):
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)
