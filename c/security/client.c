#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#define PORT 8080


void recv_text(int client, char* buffer) {
    int valread = read(client, buffer, 1024 - 1);
}

void send_text(int client, char* message) {
    send(client, message, strlen(message), 0);
    
}

int main(int argc, char const* argv[]) {
    int status, client_fd;
    struct sockaddr_in serv_addr;
    char* hello = "Hello from client";
    char buffer[1024] = { 0 }; //sets bytes to zero to avoid housing random data
    if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("Socket creation error\n");
        return -1;
    }
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr) <= 0) {
        printf("Invalid address\n");
        return -1;
    }
    if ((status = connect(client_fd, (struct sockaddr*)&serv_addr.sin_addr, sizeof(serv_addr))) < 0) {
        printf("Connection failed\n");
        return -1;
    }
    send_text(client_fd, hello);
    printf("Message sent\n");
    recv_text(client_fd, buffer);
    printf("%s\n", buffer);
    close(client_fd);
    return 0;
}
