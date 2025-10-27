import socket as netcom
from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import os
import datetime
import tarfile

curusr = os.path.expanduser("~")

chnk_sze = 0
head_sze = 100
verbose = "1"
logging = "1"
save_recent = "1"
confirm = "0"
server_ip = "127.0.0.1"
server_port = "12400"
install_path = curusr+"/.zinapp/zget"
global_install_path = "/usr/local/bin"
config_path = curusr+"/.zinapp/zget"
app_cache = curusr+"/.zinapp/zget/cache"

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+".zinapp")

attr_dict = {"verbose": verbose, "logging": logging, "save_recent": save_recent, "confirm": confirm, "server_ip": server_ip, "install_path": install_path, "config_path": config_path, "app_cache": app_cache}

attr_info = {
    "verbose": "Changing this to 0 (default is 1) will stop zget from telling you information about whats being installed and where.",
    "logging": "Changing this to 0 (default is 1) will stop zget from logging commands and information about retrived files. All of this data is local, never shared",
    "save_recent": "Changing this to 0 (default is 1) will stop zget from saving recently changed files. This is in place incase i push a bad update, using the 'undo' command will rollback the most recent update",
    "confirm": "Changing this to 1 (default is 0) will make zget confirm any changes to files when updating or installing",
    "server_ip": "The IP addess of the server you want to download your apps from",
    "install_path": f"The path your files will be installed to (default is {install_path}/apps)",
    "config_path": f"The path for the zget configuration file (default is {config_path})",
    "app_cache": f"Where recenly removed files are stored (default is {app_cache})",
    "global_install_path": f"To call an app from the commandline they need to be installed in {global_install_path}. This option is currently not able to be changed",
    "listretr": "Updates the app list so it has the information on the newest versions of installed apps and information on all the avalible apps",
    "install": "What do you think?",
    "reconfigure": "Edit the configuration file",
    "apps": "Lists currently installed apps",
    "reinstall": "Reinstalls an app. It first purges the directory and then reinstalls whatever version of the app your currently on",
    "private-policy": "zget does not collect any data at all in exception of commands. We do not collect IP address, port, location, or retrived files\nFor error logging we do collect the command you used and the error given by the server, but not the file information or what your retriving although that information can be found in the command.\nzget logs information locally including the command you used, when you used it, and the response from the server. However this is not shared and can be disabled. Its enabled so we can backtrace issues if they are reported"
}

ext_list = [".py", ".c", ".cpp"]

server = netcom.socket(ipv4, tcp)

"""UTILS"""

def frmsrv(string):
    return f"***\n{string}\n***"

def helpcmds(*string):
    print("for more help, type more-help.")
    for item, func in cmd_list.items():
        print(item)

def cleanup(name):
    os.remove(f"{app_cache}/{name}")

def uncompress(name, glb_inst):
    with tarfile.open(f"{app_cache}/{name}", 'r:gz') as tar:
        tar.extractall(path=f"{install_path}/apps")
    if glb_inst:
        for item in os.listdir(f"{install_path}/apps/{name}"):
            for curr_app in os.listdir(global_install_path):
                if name == curr_app:
                    return print("This app has been installed locally but is not callable from the commandline.\nWhen looking in the system-wide applications folder there was a duplicate application. Since this could be a critical file I will not overwrite it.\nThe only solution to this, is to ask the owner of the server your retriving from to change the name of the root folder of the application.")
            for ext in ext_list:
                if ext in item:
                    item_ext = item
                    item = item.strip(ext)
                    is_scr = False
                    break
                else:
                    is_scr = True
            try:
                if is_scr:
                    with open(f"{install_path}/apps/{name}/{item}", "r") as file:
                        script = file.read()
                        with open(f"{global_install_path}/{name}", "w") as file_install:
                            file_install.write(script)
                else:
                    with open(f"{install_path}/apps/{name}/{item_ext}", "rb") as file:
                        script = file.read()
                        with open(f"{global_install_path}/{name}", "wb") as file_install:
                            file_install.write(script)
                os.chmod(f"{global_install_path}/{name}", 0o755)
            except Exception as e:
                print(f"The file you have attempted to install is not a script file.\nEither A: this file is a non-script-like file (image, video, audio) that is named 'main' or some variation\nOr B: The file is corrupt and/or for some reason a different error occured.\nError: {e}")
def log(inp):
    if int(logging):
        with open(f"{config_path}/log.txt", "a") as file:
            file.write(f"{datetime.datetime.now}: {inp}\n")
    else:
        pass
def helpy(server, cmd):
    if "help" in cmd:
        return print("\nCommands: help, listretr, install, reinstall, update, list-apps, list-aval, list-upd\n\nFor more information, call help again but with a phrase.\n\nAvaliable phrases (excluding the commands listed): verbose\nlogging\nsave_recent\nconfirm\nserver_ip\ninstall_path\nglobal_install_path\nconfig_path\napp_cache\n")
    if cmd:
        result = attr_info.get(cmd)
        if result:
            print(result)
        else:
            print("Phrase does not exist")

def app_listupd(server, cmd): #updates local app list from server
    server.send(cmd.encode("utf-8"))
    with open(f"{config_path}/app_list.txt", "w") as file:
        print("requesting list data from server")
        list_data = server.recv(2048).decode("utf-8")
        print("data recived, writing to file")
        file.write(list_data)
    print("data written")

"""APPCTRL"""

def update(server, name):
    return

def app_get(server, name): #installs app
    curr_apps = os.listdir(f"{install_path}/apps")
    for item in curr_apps:
        if name == item:
            return print(f"{name} is already installed.")
    print(f"contacting server to install {name}")
    server.send(f"install {name}".encode("utf-8"))
    datalen = server.recv(head_sze).decode("utf-8")
    name = server.recv(int(datalen))
    if name:
        name = name.decode("utf-8")
        if "err" in name:
            return print(name)

    elif "##invalid command" in name:
        return print("executed bad command, the server and clients code/version may be out of sync.")
    file_size = server.recv(head_sze).decode("utf-8")
    print(f"installing {name}, size is {int(file_size)} bytes")
    file_size = int(file_size)
    bytes_recv = 0
    with open(f"{app_cache}/{name}", "wb") as file:
        while bytes_recv < file_size:
            chunk = server.recv(min(chnk_sze, file_size - bytes_recv))
            print(f"writing chunk, bytes recived is {bytes_recv}, left to write: {file_size - bytes_recv}")
            if not chunk:
                break
            file.write(chunk)
            bytes_recv += len(chunk)
    uncompress(name, True)
    print(f"{name} installed. Cleaning up installation files")
    cleanup(name)

def list_global(server, cmd): #lists all avaliable apps for download
    server.send(cmd.encode("utf-8"))
    result = server.recv(2048).decode("utf-8")
    if "##invalid command" in cmd:
        return print("executed bad command, the server and clients code/version may be out of sync.")
    if result:
        return print(frmsrv(result))
    else:
        print("nothing sent?")  
    
def config(*cmd):
    print("What attribute would you like to edit?")
    for title, value in attr_dict.items():
        print(f"{title}\n")
    while True:
        inp = input("*>>> ")
        if inp == "save":
            break
        if inp in attr_dict.keys():
            val = input(f"Selected {inp}.\nSet value: ")
            if inp == "verbose" or inp == "logging" or inp == "save_recent" or inp == "confirm":
                if val == "0" or val == "1":
                    attr_dict[inp] = val
                else:
                    print("That attribute needs to be a binary value")
            else:
                attr_dict[inp] = val
        print("Value changed, type 'save' to save changes.")
    
    with open(f"{config_path}/zget.conf", "w") as file:
        file.write('')
    with open(f"{config_path}/zget.conf", "a") as file:
        for title, item in attr_dict.items():
            file.write(f"{title} = {item}\n")
        print("Write succesful")
    
def list_local(*cmd): #lists installed apps
    apps = os.listdir(f"{install_path}/apps")
    if not apps:
        print("You have no apps installed")
    else:
        for i in apps:
            print(f"{i}\n")
def reinstall(name):
    return

def remove(server, name):
    inp = input(f"Are you sure you want to remove {name}?\n>>> ")
    if not "y" in inp:
        return print(f"{name} not removed")
    os.remove(f"{install_path}/apps/{name}")
    if name in os.listdir(f"{install_path}/apps"):
        return print("failed to remove file")
    else:
        return print(f"{name} has been removed")
def server_connect(server):
    global chnk_sze
    while True:
        try:
            print("Connecting to server..")
            server.connect((server_ip, int(server_port)))
            connected = server.recv(128).decode("utf-8")
            connected, chnk_sze = connected.split("|")
            chnk_sze = int(chnk_sze)
            if connected == "connected!":
                print("Connected established")
            break
        except Exception as e:
            err = f"Error connecting to server: {e}\n"
            print(err)
            with open(f"{install_path}/log.txt", "a") as file:
                file.write(err)
            break
def list_list(server, *arg):
    with open(f"{config_path}/app_list.txt", "r") as file:
        for i in file.readlines():
            if i != '\n':
                print(i.strip('\n'))

cmd_list = {"listretr": app_listupd, "install": app_get, "reinstall": reinstall, "purge": remove, "update": update, "reconfigure": config, "list-apps": list_local, "list-aval": list_global, "list-upd": list_list,"help": helpcmds, "more-help": helpy}


try:
    with open(f"{config_path}/zget.conf", "r") as file:
        for line in file.readlines():
            word, num = line.split("=")
            attr_dict[word.strip()] = num.strip()
except Exception as e:
    #print(e)
    print("Looks like this is your first time running zget. I will create the directories and config files.")   
    print(f"Generating the install directory in {install_path}")
    os.makedirs(install_path, exist_ok=True)
    print(f"Generating the application directory in {install_path}/apps")
    os.makedirs(f"{install_path}/apps", exist_ok=True)
    print(f"Generating the configuration directory in {config_path}")
    os.makedirs(config_path, exist_ok=True)
    print(f"Generating the cache directory in {app_cache}")
    os.makedirs(app_cache, exist_ok=True)
    print("Generating config..")
    with open(f"{config_path}/zget.conf", "a") as file:
        print("Writing attribute: verbose")
        file.write(f"verbose = {verbose}\n")
        print("Writing attribute: logging")
        file.write(f"logging = {logging}\n")
        print("Writing attribute: save_recent")
        file.write(f"save_recent = {save_recent}\n")
        print("Writing attribute: confirm")
        file.write(f"confirm = {confirm}\n")
        print("Writing attribute: server_ip")
        file.write(f"server_ip = {server_ip}\n")
        print("Writing attribute: install_path")
        file.write(f"install_path = {install_path}\n")
        print("Writing attribute: config_path")
        file.write(f"config_path = {config_path}\n")
    with open(f"{config_path}/log.txt", "w") as file:
        print("Generating log.txt")
        file.write("")
    log("First time start successful")

server_connect(server)
print("zget shell active. Use ctrl-c to exit. Do not exit while an install is active\ninstalled programs are located in ~/.local, type 'help' for more info.")

while True:
    cmd = input(">>> ")
    log(cmd)
    if " " in cmd:
        cmd, flag = cmd.split(" ")
    else:
        flag = cmd
    xcute = cmd_list.get(cmd)
    if xcute:
        result = xcute(server, flag)
        log(result)
    else:
        print("That is not an avalible command. Type help for more.")
