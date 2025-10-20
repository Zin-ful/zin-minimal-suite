from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
import time

users = []
usernames = {}
clients_lock = task.Lock()
calling = 0

codes = {"call-start": "001",  "call-confirmation": "002", "call-end": "003", "call-timeout": "004", "err": "000"}

host_ip = "0.0.0.0"
port = 10874

buffer_size = 2048
timeout_limit = 15

self = netcom.socket(ipv4, tcp)
self.bind((host_ip, port))





def init_client(client, addr):
    global calling, buffer_size
    waittime = 0
    print(f"thread started for {addr}")
    addr_id = str(addr)
    user_id, user_ip = addr_id.split(",")
    user_ip = user_ip.strip("(").strip("'").strip(")")
    if not ack(client, 0):
        print(f"sync err with client {addr}")
        return
    else:
        ack(client, 1)
    print("waiting for caller ID")
    user_info = recv_text(client)
    caller, buffer_size = user_info.split("&")
    buffer_size = int(buffer_size)
    if caller:
        usernames.update({caller: client})
        print("caller added")
    with clients_lock:
        users.append(client)
    ack(client, 1)
    listener = None
    while not listener:
        print("waiting for call request")
        listener = recv_text(client)
        time.sleep(1)
        print("call request incoming")
    while listener not in usernames.keys():
        print(f"waiting for other user. time waited = {waittime} & timeout limit = {timeout_limit}")
        time.sleep(1)
        waittime += 1
        if waittime >= timeout_limit:
            send_text(client, codes["call-timeout"])
            print("call timed out")
            return
    calling = 1
    confirm = send_call_request(listener, buffer_size)
    if confirm:
        pass
    elif not confirm:
        send_text(client, codes["call-end"])
        print("call rejected")
        returns
    start_call(client, listener, buffer_size)

def send_call_request(listener, buffer_size):
    name = listener
    listener = usernames[listener]
    send_text(listener, codes["call-start"]+":"+name)
    confirm = recv_text(listener)
    while not confirm:
        time.sleep(0.2)
    if confirm == codes["call-confirmation"]:
        return 1
    elif confirm == codes["call-end"]:
        return 0
    


def send_text(client, string):
    print(f"sending {string}")
    client.send(string.encode("utf-8"))

def ack(client, mode):
    if mode:
        print("sending ack")
        client.send("ACK".encode("utf-8"))
    else:
        print("reciving ack")
        is_ack = client.recv(3).decode("utf-8")
        if is_ack.strip() == "ACK" or is_ack.strip() == "REQ":
            return True

def recv_text(client):
    print("recieving...")
    data = client.recv(128).decode("utf-8")
    print("Recv + ", data)
    return data


def start_call(caller, listener, buffer):
    global calling
    listener = usernames[listener]
    caller_thread = task.Thread(target=send_audio_to_user, args=[caller, listener, buffer])
    listener_thread = task.Thread(target=send_audio_to_listener, args=[caller, listener, buffer])
    try:
        while True:
            listener.send(codes["call-start"])
            if ack(listener, 0):
                break
        caller_thread.start()
        listener_thread.start()
        while calling:
            pass
    except BrokenPipeError:
        pass
    finally:
        pass

def send_audio_to_caller(caller, listener, buffer):
    listener = usernames[listener]
    while True:
        send_to_listener = caller.recv(buffer)
        print(send_to_listener)
        if send_to_listener:
            listener.send(send_to_listener)

def send_audio_to_listener(caller, listener, buffer):
    listener = usernames[listener]
    while True:
        send_to_caller = listener.recv(buffer)
        print(send_to_caller)
        if send_to_caller:
            caller.send(send_to_caller)



while True:
    try:
        print("listening..")
        self.listen(10)
        client_socket, addr = self.accept()
        client_thread = task.Thread(target=init_client, args=[client_socket, addr])
        client_thread.start()
    except Exception as e:
        print(e)
        exit()
