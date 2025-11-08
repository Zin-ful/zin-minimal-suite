#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
#include "socketops.h"

int str_size(const char *string) {
    int i = 0;
    while (string[i] != '\0') {
        i++;
    }
    return i;
}

ssize_t sendd(int sock, const char *msg) {
    return send(sock, msg, str_size(msg), 0);
}

ssize_t recvd(int sock, char* buffer, size_t size) {
    for (size_t i = 0; i < size; i++) {
        buffer[i] = 0;
    }
    ssize_t bytes = recv(sock, buffer, size - 1, 0);
    if (bytes < 0) {
        perror("Error in socketops.c - recv");
    }
}
