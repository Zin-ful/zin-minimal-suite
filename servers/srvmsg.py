from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import socket as netcom
import threading as task
import datetime
import os

"""
FIX

Server doesnt know when clients ctrl-C - should be fixed as of 1/25/26
In direct message, make sure the direct messanger doesnt recieve group chat texts
In direct message, make sure users dont see the system connected message
Test missed message sending
Add file sending
"""

def gen_update():
    update_tuple = (
    "Implement missed messages",
    "Direct texting has receivied the same updates as group chat",
    "Server can now reconnect clients without crashing",
    "client version is now 4.0!"
    )
    msg = ""
    for item in update_tuple:
        msg += item + "\n"
    return msg

server_version = 3.5

updatemsg = f"server.message.from.server." + "Server Compatability: 4.0 - 4.2\nTo-Do List: " + gen_update()


conf_path = "/opt/zinapp/ztext_srvr"
port = 34983
ip = "0.0.0.0"
passwd = "admin"
linky = "none"
contact = "none"
header_size = 10

missed_path = "/opt/zinapp/ztext/missed/" 
file_path = "/opt/zinapp/ztext/cache/"
attr_dict = {"contact": contact, "link": linky, "passwd": passwd}

if not "zinapp" in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")

if not "ztext" in os.listdir("/opt/zinapp"):
    os.mkdir("/opt/zinapp/ztext")

if not "missed" in os.listdir("/opt/zinapp/ztext"):
    os.mkdir("/opt/zinapp/ztext/missed")
if not "cache" in os.listdir("/opt/zinapp/ztext"):
    os.mkdir("/opt/zinapp/ztext/cache")

def load():
    try:
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for line in file.readlines():
                name, val = line.split("=", 1)
                attr_dict[name.strip()] = val.strip()
    except Exception as e:
        #print(e)
        os.makedirs(conf_path, exist_ok=True)
        with open(f"{conf_path}/msg_server.conf", "a") as file:
            for name, val in attr_dict.items():
                file.write(f"{name} = {val}\n")
        #print("generating report file")
        with open(f"{conf_path}/reports.txt", "w") as file:
            file.write("")
        with open(f"{conf_path}/missed.txt", "w") as file:
            #print("generating missed messages file")
            file.write("")

server = netcom.socket(ipv4, tcp)
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
server.bind((ip, port))



users = []
user_direct = []
user_file = []
user_call = []
users_name = {}
clients_lock = task.Lock()

def send(client, data):
    try:
        head = str(len(data)).zfill(header_size)
        data = head + data
        print(f"sending data to {users_name.get(client)}: {data}")
        client.send(data.encode("utf-8"))
        return 1
    except (BrokenPipeError, ConnectionResetError):
        client_end(client)
        return 0

def receive(client):
    try:
        name = users_name.get(client)
        if not name:
            name = "Unknown"
        data_received = b''
        print("receiving header..")
        packet_size = client.recv(header_size).decode("utf-8")
        if not packet_size:
            client_end(client)
            return 0
        packet_size = int(packet_size)
        print(f"header size is: {packet_size}")
        while len(data_received) < packet_size:
            data_received += client.recv(packet_size - len(data_received))
            print(f"data being received from {users_name.get(client)}: {packet_size} | {len(data_received)} = {data_received}")
        if not data_received:
            client_end(client)
            return 0
        data_received = data_received.decode("utf-8")
        return data_received
    except (OSError):
        client_end(client)
        return 0

def send_file(client, name):
    try:
        file_size = os.path.getsize(file_path + name)
        head = str(file_size).zfill(header_size)
        client.send(head.encode("utf-8"))
        sent_bytes = 0
        with open(file_path + name, "rb") as file:
            while sent_bytes < file_size:
                chunk = file.read(4096)
                if not chunk:
                    break
                client.send(chunk)
                sent_bytes += len(chunk)
                print(f"sent {sent_bytes}/{file_size} bytes of {name}")
        
        print(f"file {name} sent successfully, total: {sent_bytes} bytes")
        return 1
    except (BrokenPipeError, ConnectionResetError, OSError):
        client_end(client)
        return 0

def receive_file(client, name):
    try:
        data_received = b''
        print("receiving file header..")
        packet_size = client.recv(header_size).decode("utf-8")
        if not packet_size:
            client_end(client)
            return 0
        packet_size = int(packet_size)
        print(f"file size is: {packet_size}")
        
        with open(file_path + name, "wb") as file:
            while len(data_received) < packet_size:
                chunk = client.recv(min(4096, packet_size - len(data_received)))
                if not chunk:
                    break
                file.write(chunk)
                data_received += chunk
                print(f"writing data from socket: {packet_size} | {len(data_received)}")
        
        print(f"Received file {name}, size: {len(data_received)} bytes")
        return 1
    except (OSError):
        client_end(client)
        return 0

def contact(client_socket, msg):
    return f"server.message.from.server.{attr_dict['contact']}"

def link(client_socket, msg):
    return f"server.message.from.server.{attr_dict['link']}"

def helpy(client_socket, msg):
    items = ""
    for name, val in commands.items():
        items += "\n"
    return "server.message.from.server." + items

def bug_report(client_socket, msg):
    send(client_socket, "server.message.from.server.Please submit the issue you encountered and the steps to reproduce (if any)")
    bug = receive(client_socket)
    if bug:
        with open(f"{conf_path}/reports.txt", "a") as file:
            file.write(f"{datetime.datetime.now()} report: {bug}\n")
        return "server.message.from.server.Submitted!"
    else:
        return "server.message.from.server.you cant exactly submit a bug without the.. yknow.. bug?"

def list_users(client_socket, msg):
    if msg:
        msg = ""
        for i in users_name.values():
            msg += f"{i}\n"
        return f"server.message.from.server. {msg}"

def updlink(client_socket, msg):
    send(client_socket, "server.message.from.server.Updating link. Submit your response in this format: {password}:{link}")
    response = receive(client_socket)
    if response:
        try:
            auth, link = response.split(":", 1)
        except:
            return "server.message.from.server.improper format, maybe forgot the ':' ?"
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for item in file.readlines():
                if "passwd" in item:
                    trash, passwd = item.split("=", 1)
        if passwd.strip() == auth.strip():
            attr_dict["link"] = link
            with open(f"{conf_path}/msg_server.conf", "w") as file:
                file.write("")
            with open(f"{conf_path}/msg_server.conf", "a") as file:
                for name, val in attr_dict.items():
                    file.write(f"{name} = {val}\n")
        else:
            return "server.message.from.server.invalid password"
    else:
        return "server.message.from.server.you know you have to say something, right?"
    return "server.message.from.server.link updated"

def updcontact(client_socket, msg):
    send(client_socket, "server.message.from.server.Updating contact information. Submit your response in this format: {password}:{contact}")
    response = receive(client_socket)
    if response:
        try:
            auth, cont = response.split(":", 1)
        except:
            return "server.message.from.server.improper format, maybe forgot the ':' ?"
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for item in file.readlines():
                if "passwd" in item:
                    trash, passwd = item.split("=", 1)
        if passwd.strip() == auth.strip():
            attr_dict["contact"] = cont
            with open(f"{conf_path}/msg_server.conf", "w") as file:
                file.write("")
            with open(f"{conf_path}/msg_server.conf", "a") as file:
                for name, val in attr_dict.items():
                    file.write(f"{name} = {val}\n")
        else:
            return "server.message.from.server.invalid password"
    else:
        return "server.message.from.server.you cant just say nothing"
    return "server.message.from.server.contact updated"

def updpasswd(client_socket, msg):
    send(client_socket, "server.message.from.server.Updating admin password. Submit your response in this format: {oldpass}:{newpass}")
    response = receive(client_socket)
    if response:
        try:
            old, new = response.split(":", 1)
        except:
            return "server.message.from.server.improper format, maybe forgot the ':' ?"
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for item in file.readlines():
                if "passwd" in item:
                    trash, passwd = item.split("=", 1)
        if old.strip() == passwd.strip():
            attr_dict["passwd"] = new
            with open(f"{conf_path}/msg_server.conf", "w") as file:
                file.write("")
            with open(f"{conf_path}/msg_server.conf", "a") as file:
                for name, val in attr_dict.items():
                    file.write(f"{name} = {val}\n")
        else:
            return "server.message.from.server.old password is invalid"
    else:
        return "server.message.from.server.not one for words, are ya?"

    return "server.message.from.server.password updated"

def handle_upload(client_socket, msg):
    saved_name = users_name[client_socket]
    name = receive(client_socket)
    name = name.replace(" ", "_")
    print(f"client attempting to upload {name}")
    if name in os.listdir(file_path):
        send(client_socket, "server.message.from.server.ALREADY_EXISTS")
        i = 0
        while name in os.listdir(file_path):
            i += 1
            name = f"{i}-{name}"
    else:
        send(client_socket, "server.message.from.server.CONTINUE")
    receive_file(client_socket, name)
    with clients_lock:
        users_copy = users[:]
    for other_client in users_copy:
            if other_client != client_socket:
                send(other_client, f"server.message.from.server.The user '{saved_name}' has uploded the file {name}\nenter your file browser to download.")
    return f"server.message.from.server.{name} uploaded and users have been notified."

def handle_download(client_socket, msg):
    saved_name = users_name[client_socket]
    name = receive(client_socket)
    if name.strip() not in os.listdir(file_path):
        return "server.message.from.server.NOT_FOUND"
    send_file(client_socket, name.strip())
    with clients_lock:
        users_copy = users[:]
    for other_client in users_copy:
            if other_client != client_socket:
                send(other_client, f"server.message.from.server.{name} has been downloaded by {saved_name}")
    return "server.message.from.server.File has been downloaded"

def list_files(client_socket, msg):
    if not os.listdir(file_path):
        return "server.message.from.server.NO_FILES"
    files = ""
    for item in os.listdir(file_path):
        files += item + " "
    return files

commands = {"get-file":handle_download, "list-file":list_files,"send-file":handle_upload, "bug-report":bug_report,"get-users": list_users,"get-link": link, "get-contact": contact, "help":helpy, "set-link": updlink, "set-contact": updcontact, "set-password": updpasswd}

def log(client_socket, msg):
    if msg:
        with open(f"{conf_path}/log.txt", "a") as file:
            file.write(f"from {client_socket}: {msg}\n")

def save_missed(name, message):
    with open(missed_path+f"{name}.txt", "a") as file:
        file.write(message+"\n")

def check_missed(name):
    missed = None
    if f"{name}.txt" not in missed_path:
        return None
    with open(missed_path+f"{name}.txt", "r") as file:
        check = file.readlines()
        while True:
            if len(check) < 15:
                for item in check:
                    missed += item
            else:
                i = 0
                while i < 10:
                    check.pop(i)
                    i += 1
    if missed:
        return missed
    else:
        return None

def direct_send(message, source_user):
    try:
        username, message = message.split(":", 1)
    except:
        return
    username = username.strip("@")
    for id, user in users_name.items():
        if username.lower().strip() == user.lower().strip():
            print(f"sending DM to {source_user}")
            send(id, f"\n@{source_user} (direct): {message}\n")
            break
    save_missed(username, message)
            
def messenger(client_socket, addr):
    addr_id = str(addr)
    user_id, user_ip = addr_id.split(",")
    user_ip = user_ip.strip("(").strip("'").strip(")")
    user_id = user_ip.strip("(").strip("'").strip(")")

    username = receive(client_socket)
    if username:
        users_name.update({client_socket: username})
    print(f"user: {username} connected from {client_socket}")
    type = receive(client_socket) 
    print(f"User type is: {type}")
    if type == "d":
        print("appended to direct")
        user_direct.append(client_socket)
    elif type == "f":
        print("appended to file")
        user_file.append(client_socket)
    elif type == "c":
        print("appended to call")
        user_call.append(client_socket)
        print("passing to init_call")
        init_call(username, client_socket, addr)
        print("returning..")
        return
    
    if client_socket not in user_file:
        send(client_socket, str(len(users)))
    print(f"user connected: {addr}")
    with clients_lock:
        users.append(client_socket)
    #prevent sending inside lock, it will significantly slow the network down
    with clients_lock:
        users_copy = users[:]
    startmsg = f"server.message.from.server.users: {len(users)} !SYSTEM MESSAGE: user connected: {users_name[client_socket]}"
    for other_client in users_copy:
        if other_client != client_socket or (other_client not in user_direct and other_client != client_socket) or (other_client not in user_file and other_client != client_socket) or (other_client not in user_call and other_client != client_socket):
            if not send(other_client, startmsg):
                return

    if client_socket not in user_file:
        print("sending update message")
        if not send(client_socket, updatemsg):
            return
    print("Sent")
    missed = check_missed(username)
    if missed:
        client.send("SYSTEM MISSED MESSAGES\n{missed}")
    while True:
        message = receive(client_socket)
        if not message:
            break
        #calling inside the while true loop to update before msg sends
        with clients_lock:
            users_copy = users[:]
        message += '\n'
        if message[0] == "@":
            direct_send(message, users_name.get(client_socket))
            continue
        if client_socket in user_direct:
            continue
        if "server.main." in message and '"' not in message:
            cmd = message.replace("server.main.", "")
            log(client_socket, cmd)
            xcute = commands.get(cmd.strip())
            print("Getting command..")
            if xcute:
                message = xcute(client_socket, message)
            else:
                message = "server.message.from.server.invalid"
            log(client_socket, message)
            if not send(client_socket, message):
                break
            continue
        else:
            message = f"\n@{users_name.get(client_socket)}: {message}\n"
        if len(users) <= 1:
            with open(f"{conf_path}/missed.txt", "a") as file:
                file.write(f"{message}\n")
        
        for other_client in users_copy:
            if other_client != client_socket:
                send(other_client, message)

def client_end(client):
    print("ending client")
    
    with clients_lock:
        if client not in users[:]:
            print("client already removed")
            return        
        username = users_name.get(client, "Unknown")
        users.remove(client)
        if client in users_name:
            del users_name[client]
        if client in user_direct:
            user_direct.remove(client)
    try:
        client.close()
    except:
        pass
    print(f"client disconnected: {username}")
    end_msg = f"server.message.from.server.users: {len(users)} !SYSTEM MESSAGE: user DISconnected: {username}"
    for user in users[:]:
        try:
            send(user, end_msg)
        except:
            pass

"""Pasting in the logic from the old calling server"""

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

def init_call(username, client, addr):
    global buffer_size
    waittime = 0
    print(f"moved {username}:{addr} to calling thread")
    try:
        while True:
            listener = None
            print(f"waiting for call request from {username}")
            
            try:
                listener_username = receive(client)
            except:
                print(f"{username} disconnected")
                break
                
            if not listener:
                print(f"{username} disconnected or sent empty request")
                break
                
            listener += "-call"
            print(f"call request from {username} to {listener_username}")

            waittime = 0
            while not check_for_listener(listener):
                print(f"waiting for {listener_username}. time waited = {waittime} & timeout limit = {timeout_limit}")
                time.sleep(1)
                waittime += 1
                if waittime >= timeout_limit:
                    send_text(client, codes["call-timeout"])
                    print("call timed out")
                    break
                    
            if check_for_listener(listener_username):
                listener_socket = get_socket(listener_username)
                confirm = send_call_request(caller, listener_socket, buffer_size)
                if confirm:
                    send_text(client, codes["call-confirmation"])
                    start_call(caller, listener_socket, buffer_size)
                else:
                    send_text(client, codes["call-end"])
                    print("call rejected")
                        
    except Exception as e:
        print(f"Error with client {caller}: {e}")
    finally:
        cleanup_client(client, caller)

def check_for_listener(name):
    with clients_lock:
        users_copy = users[:]
    for sock, other_name in users_name.items():
        if name == other_name:
            return 1
    return 0

def get_socket(name):
    for sock, other_name in users_name.items():
        if name == other_name:
            return sock

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


load()
server.listen(10)
print(f"server listening on ip: {ip} and port {port}")
        
while True:
    try:
        client_socket, addr = server.accept()
        client_thread = task.Thread(target=messenger, args=(client_socket, addr))
        client_thread.start()
    except Exception as e:
        pass
