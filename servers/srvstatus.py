from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
import subprocess as proc
import time

port_list = [10592, 10874, 23512, 39562, 25415, 
34983, 41742, 49652, 54574, 61431]

app_ports = {"wg_key": 10592, "drive": 25415,
"msg": 34983, "mail": 52311,"shell":39562, "call": 10874,
"program-editor": 49652, "zapp": 41742,
"video_server": 61431, "library_server": 0}

status = {}

for name, cache in app_ports.items():
    status.update({name: 0}) 

"""status = {"wg_key": 0, "drive": 0, "msg": 0, 
"mail": 0, "shell": 0, "call": 0, 
"program-editor":0, "zapp": 0, 
"video_server": 0, "library_server": 0}
"""

port = 23512

server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")

def init():
    while True:
        try:
            print("listening...")
            server.listen(20)
            client, client_ip = server.accept()
            print(f"client accepted: {client_ip}")
            thread_client = task.Thread(target=client_start, args=[client])
            thread_client.start()
        except Exception as e:
            print(e)


def status_check(port):
    app_status = proc.run([f"netstat -l | grep :{port}"], shell=True, capture_output=True, text=True)
    if app_status.stdout:
        return 1
    else:
        return 0

def client_start(client):
    while True:
        try:
            ack = client.recv(3).decode("utf-8")
            if not ack:
                continue
            all_status = ""
            for key, val in status.items():
                status[key] = status_check(app_ports[key])
                if status[key]:
                    all_status += f"{key} = {status[key]}\n"
                else:
                    print(f"{key} not found at {val}")
            if all_status:
                print("sending status")
                client.send(all_status.encode("utf-8"))
            else:
                client.send("\nno servers active\n".encode("utf-8"))

        except Exception as e:
            print(e)
            client.close()
            break

init()