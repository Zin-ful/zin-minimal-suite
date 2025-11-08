#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "socketops.h"

#define PORT 8080
#define BUFFER_SIZE 1024

int conn_limit = 3;

int main() {
    int server_fd, new_socket; //file descriptor
    struct sockaddr_in address; //socket struct
    int opt = 1;
    int addrlen = sizeof(address); 
    char buffer[BUFFER_SIZE];
    
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("socket opt failed");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("socket bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, conn_limit) < 0) {
        perror("server listen failed");
        exit(EXIT_FAILURE);
    }

    printf("server started and is listening for %d clients\n", conn_limit);

    if ((new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen))) {
        perror("connection attempt:");
        exit(EXIT_FAILURE);
    }
    
    printf("connection accepted\n");
    recvd(new_socket, buffer, sizeof(buffer));
    printf("%s\n", buffer);
    sendd(new_socket, "ack");
    close(new_socket);
    close(server_fd);
    return 1;
}
