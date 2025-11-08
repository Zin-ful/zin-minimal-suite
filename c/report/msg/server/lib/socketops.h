#ifndef SOCKETOPS_H
#define SOCKETOPS_H

int str_size(const char *string);
ssize_t sendd(int sock, const char *msg);
ssize_t recvd(int sock, char* buffer, size_t size);
#endif
