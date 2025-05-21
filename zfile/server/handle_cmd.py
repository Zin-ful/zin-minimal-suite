import base64
import os
import sys
import subprocess
import threading as task
path = "storage"
root = "storage"
priv = ''
user = ''
conn = None
skip = 0

def pass_user(name):
    global path, root, user
    if "admin" not in name:
        path = f"storage{name}" #from login so we can handle multiple users
        root = f"storage{name}"
    user = name

"""file interaction"""
def get(file_name):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    trash, file_ext = file_name.split(".")
    file_ext = "." + file_ext
    if not any('/' in char for char in file_name):
        file_name = '/' + file_name
    to_down = path + str(file_name)
    if any(file_name.strip('/') in files for files in os.listdir(path)):
        try:
            if any(file_ext in files for files in ext_list):
                with open(to_down, 'r') as file:
                    filedata = file.read()
                    result = file_name +  '!:DATA:!' + filedata
            else:
                with open(to_down, 'rb') as file:
                    filedata = file.read()
                    filedata = base64.b64encode(filedata).decode('utf-8')
                    result = file_name + '!:DATA:!' + filedata
        except Exception as e:
            result = e
    else:
        result = f'file {file_name} not found: {path}{file_name}\n\n{os.listdir(path)}'
    return result


def send(data):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    trash, file_ext = file_name.split(".")
    file_ext = "." + file_ext
    if not any('/' in char for char in file_name):
        file_name = '/' + file_name
    to_down = path + str(file_name)
    if any(file_name.strip('/') in files for files in os.listdir(path)):
        try:
            if any(file_ext in files for files in ext_list):
                with open(to_down, 'r') as file:
                    filedata = file.read()
                    result = file_name +  '!:DATA:!' + filedata
            else:
                with open(to_down, 'rb') as file:
                    filedata = file.read()
                    filedata = base64.b64encode(filedata).decode('utf-8')
                    result = file_name + '!:DATA:!' + filedata
        except Exception as e:
            result = e
    else:
        result = f'file {file_name} not found: {path}{file_name}\n\n{os.listdir(path)}'
    return result

def send_in_chunk(recv_cmd):
    global skip
    if path == root:
        return "cannot upload files to /storage, choose a folder"
    if not skip:
        ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
        file_name, data = data.split("!:DATA:!")
        trash, file_ext = file_name.split(".")
        if any(file_name.strip("/") in files for files in os.listdir(path)):
            return "file already exists, use update to overrite files"
        elif not any(file_name in files for files in os.listdir(path)):
            skip = 1
            pass
        try:
            if any(file_ext in files for files in ext_list):
                with open(f"{path}{file_name}", "a") as file:
                    file.write(data)
            else:
                data = base64.b64decode(data)
                with open(f"{path}{file_name}", "ab") as file:
                    file.write(data)
        except Exception as e:
            return f"file failed to download due to these reasons: {e}"

def update(data):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    file_name, data = data.split("!:DATA:!")
    trash, file_ext = file_name.split(".")
    if not any(file_name.strip("/") in files for files in os.listdir(path)):
        return "cannot update files that dont exist, use send to upload a new file"
    elif any(file_name in files for files in os.listdir(path)):
        try:
            if any(file_ext in files for files in ext_list):
                with open(f"{path}{file_name}", "w") as file:
                    file.write(data)
            else:
                data = base64.b64decode(data)
                with open(f"{path}{file_name}", "wb") as file:
                    file.write(data)
            result = "file updated to new version"
        except Exception as e:
            return f"file failed to download due to these reasons: {e}"

    return result


def remove(file_name):
    if any('/' in char for char in file_name):
        file_name = file_name.strip("/")

    if file_name in os.listdir(path):
        try:
            subprocess.run(["rm", "-rf", f"{path}/{file_name}"])
            if file_name not in os.listdir(path):
                return f"{file_name} removed successfully"
            else:
                return f"{file_name} not removed for unknown reasons"
        except Exception as e:
            return e
    else:
        return "file not found"

def compress(file_name):
    return

def print_txt(file_name):
    return

def print_properties(file_name): #when writing and reading file, append who did it and when to a txt file in config. will have to pass name to this module
    return

def find(file_name): #search through all directories and combine all files inside into one list to for loop through and check for a file name
    root_list = os.listdir(root)
    for folder in root_list:
        current_dir = os.listdir(f"{root}/{folder}")
        for file in current_dir:
            if file_name in file:
                return f"file found in {folder}"
    return "file not found"

"""system information"""

def system(cmd):
    arg = ''
    whitelist = {
        "uptime":"uptime",
        "ip":"ip -a",
        "os":"uname -a",
        "update":"apt update",
        "shutdown":"sudo poweroff",
        "restart":"sudo restart"
        }
    """                 if str(cmd) == "os.mkdir":
                    try:
                        arg = arg.strip("/")
                        cmd(f"{root}/{arg}")
                    except FileExistError:
                        return "folder already exists"
                    except Exception as e:
                        return e
                    return "folder created"""
    for i in whitelist.keys():
        if cmd == i:
            cmd = whitelist.get(cmd)
            if ' ' in cmd:
                cmd, arg = cmd.split(' ', 1)
                cmd = "sudo " + cmd
                return subprocess.run([cmd, arg], capture_output = True, text = True).stdout
            else:
                cmd = whitelist.get(cmd)
                return subprocess.run([cmd], capture_output = True, text = True).stdout
def list_dir():
    result = ''
    total = len(os.listdir(path))
    count = 0
    for i in os.listdir(path):
        count += 1
        if count < total:
            result += i + ', '
        elif count == total:
            result += i
    return result

def make_dir(dir_name):
    if any('/' in d for d in dir_name):
        dir_name = dir_name.strip("/")
    if not dir_name in os.listdir(path):
        subprocess.run([f"mkdir {path}/{dir_name}"], shell=True)
        return "diretory created"
    else:
        return "directory already exists"
def change(dir_name):
    global path
    white_list = [user, "home","root","back",".."]
    if dir_name not in os.listdir(path) and dir_name not in white_list:
        return "that directory does not exist"
    elif "." in dir_name:
        return "cannot move into a file"
    if not any('/' in d for d in dir_name):
        dir_name = '/' + dir_name
    if dir_name in white_list:
        path = root
        result = f'directory changed to {path}'
    elif not '/storage' in dir_name:
        path = path + str(dir_name)
        result = f'directory changed to {path}'
    else:
        result = 'directory not found, might not exist'
    return result


def info(cmd_name):
    info_dict = {
        "login": "allows you to login to the server, an account needs to be created by an admin",
        "help": "lists basic commands",
        "exit": "closes the server, needs to be reopened manually",
        "create": "(admin) creates an account, default priv is 0",
        "config": "(admin) sets the server configuration",
        "promote": "(admin) promotes a users status to 1",
        "msg": "runs the message client",
        "games": "brings you to the game selection menu",
        "send": "to upload a file, cannot overwrite",
        "get": "to download a file",
        "remove": "(admin) deletes a file off the server",
        "update": "overrites an existing file",
        "print": "(admin) outputs the text content of a human readable file",
        "list": "lists the items of your current directory",
        "change": "changes your current directory location",
        "info": "provides added information on commands",
        "pwd": "prints your current directory location",
        "compress": "(admin) creates a compressed copy of a file",
        "properties": "(admin) displays the history of a file along with other information like size and who made it",
        "system": "(admin) allows the execution of whitelisted commands with the syntax: sys-command",
        "priv": "allows the edit of file permissions, so some files can be admin only"

        }
    get_info = info_dict.get(cmd_name)
    if get_info:
      return f"{cmd_name}::{get_info}"
    else:
        return f"{cmd_name} does not exist"
def pwd():
    return path

def priv():
    return
"""post login"""

def cmd_x(command, *arg):

    xcute = cmd_dict.get(command)
    if xcute:
        return xcute(*arg)#since we omit the () in the dictionary for the functions, we put it here
                    #instead that way we only call the function that the user wants
    else:
        result = 'Invalid command.'
        return result


cmd_dict = {
    "send": send,
    "get": get,
    "update": update,
    "remove": remove,
    "print": "return",
    "find": find,
    "list": list_dir,
    "makefd": make_dir,
    "change": change,
    "info": info,
    "pwd": pwd

}

def command(set_priv, cmd, *cmd2):
    global priv
    priv = set_priv #for help or other commands that use priv, dont feel like including this status as a parameter in every command
    root_list = ["sys","priv","properties","compress"]
    if set_priv == "1":
        cmd_dict.update({"sys":system,"sys-help":"return","priv":"return","properties":"return","compress":"return"})
    while True:
        if 'exit' in cmd:
            sys.exit
        if cmd in root_list and set_priv == "0":
            return "you cannot use this command"
        if cmd2:
            cmd2 =  ''.join(cmd2)
            return cmd_x(cmd, cmd2)
        if cmd:
            return cmd_x(cmd)
        return result

if __name__ == '__main__':
    cmdloop()
