from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
import time

users = []
usernames = {}
clients_lock = task.Lock()

codes = {"call-start": "001", "call-confirmation": "002", "call-end": "003", "call-timeout": "004", "err": "000"}

buffer_size = 2048
timeout_limit = 15

def cleanup_client(client, username):
    """Clean up client resources"""
    with clients_lock:
        if username and username in usernames:
            del usernames[username]
        if client in users:
            users.remove(client)
    try:
        client.close()
    except:
        pass
    print(f"Cleaned up client {username}")

def init_call(client, addr):
    global buffer_size
    waittime = 0
    caller = None
    print(f"moved {addr} to calling thread")
    
    try:
        if not ack(client, 0):
            print(f"sync err with client {addr}")
            cleanup_client(client, None)
            return
        else:
            ack(client, 1)
            
        print("waiting for caller ID")
        user_info = recv_text(client)
        if not user_info or "&" not in user_info:
            print("Invalid user info received")
            cleanup_client(client, None)
            return
            
        caller, client_buffer = user_info.split("&")
        buffer_size = int(client_buffer)
        
        if caller:
            with clients_lock:
                usernames.update({caller: client})
                users.append(client)
            print(f"caller {caller} added")
            
        ack(client, 1)
        
        while True:
            listener = None
            print(f"waiting for call request from {caller}")
            
            try:
                listener = recv_text(client)
            except:
                print(f"{caller} disconnected")
                break
                
            if not listener:
                print(f"{caller} disconnected or sent empty request")
                break
                
            print(f"call request from {caller} to {listener}")
            
            waittime = 0
            while listener not in usernames.keys():
                print(f"waiting for {listener}. time waited = {waittime} & timeout limit = {timeout_limit}")
                time.sleep(1)
                waittime += 1
                if waittime >= timeout_limit:
                    send_text(client, codes["call-timeout"])
                    print("call timed out")
                    break
                    
            if listener in usernames.keys():
                confirm = send_call_request(caller, listener, buffer_size)
                if confirm:
                    send_text(client, codes["call-confirmation"])
                    start_call(caller, listener, buffer_size)
                else:
                    send_text(client, codes["call-end"])
                    print("call rejected")
                        
    except Exception as e:
        print(f"Error with client {caller}: {e}")
    finally:
        cleanup_client(client, caller)

def send_call_request(caller_name, listener_name, buffer_size):
    listener = usernames.get(listener_name)
    if not listener:
        return 0
        
    send_text(listener, codes["call-start"]+":"+caller_name)
    
    confirm = None
    wait = 0
    while not confirm and wait < timeout_limit:
        confirm = recv_text(listener)
        if not confirm:
            time.sleep(0.5)
            wait += 0.5
            
    if confirm == codes["call-confirmation"]:
        return 1
    elif confirm == codes["call-end"]:
        return 0
    return 0

def send_text(client, string):
    try:
        print(f"sending {string}")
        client.send(string.encode("utf-8"))
    except:
        print("send failed")

def ack(client, mode):
    try:
        if mode:
            print("sending ack")
            client.send("ACK".encode("utf-8"))
            return True
        else:
            print("receiving ack")
            is_ack = client.recv(3).decode("utf-8")
            if is_ack.strip() == "ACK" or is_ack.strip() == "REQ":
                return True
            return False
    except:
        return False

def recv_text(client):
    try:
        data = client.recv(128).decode("utf-8")
        if data:
            print("Recv: ", data)
        return data
    except:
        return None

def start_call(caller_name, listener_name, buffer):
    caller = usernames.get(caller_name)
    listener = usernames.get(listener_name)
    
    if not caller or not listener:
        print("caller or listener not found")
        return
        
    call_active = [True]

    caller_thread = task.Thread(target=send_audio_to_listener, daemon=True)
    listener_thread = task.Thread(target=send_audio_to_caller, daemon=True)
    
    try:
        caller_thread.start()
        listener_thread.start()
        print(f"call started between {caller_name} and {listener_name}")
        
        while caller_thread.is_alive() and listener_thread.is_alive() and call_active[0]:
            time.sleep(0.5)
            
        call_active[0] = False
        
    except Exception as e:
        print(f"Call error: {e}")
        call_active[0] = False
    finally:
        print(f"call ended between {caller_name} and {listener_name}")

def send_audio_to_caller():
    try:
        while call_active[0]:
            send_to_caller = listener.recv(buffer)
            if not send_to_caller:
                call_active[0] = False
                break
            caller.send(send_to_caller)
    except:
        call_active[0] = False

def send_audio_to_listener():
    try:
        while call_active[0]:
            send_to_listener = caller.recv(buffer)
            if not send_to_listener:
                call_active[0] = False
                break
            listener.send(send_to_listener)
    except:
        call_active[0] = False
    

print(f"Server starting on {host_ip}:{port}")
try:
    while True:
        try:
            print("listening..")
            self.listen(10)
            client_socket, addr = self.accept()
            print(f"connection from {addr}")
            client_thread = task.Thread(target=init_client, args=[client_socket, addr], daemon=True)
            client_thread.start()
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by outer try
        except Exception as e:
            print(f"Error: {e}")
finally:
    print("\nShutting down server...")
    self.close()
    print("Server closed")
