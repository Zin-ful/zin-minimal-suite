print("Welcome to helpy!\n\n")
print("type a word or phrase in to get context on what you may be looking for")

cmd_list = ["ls [arg/name/nothing]: to list, view, or see the contents of directories/folders",
"cat [name]: to read a file and output its contents onto the screen",
"cp [name/location] [name/location] : to copy a file to another location (from -> to). cp -r will allow you to copy folders",
"mv [name/location] [name/location] : to move a file to another location (from -> to))",
"rm [name] : to remove or delete a file. use rm -rf to remove directories. deleted files cannot be recovered.",
"htop / top: views system resource usage for CPU & RAM as well as processes",
"tmux : creates a virtual terminal. KEYBINDS (ctrl+b first, then next keybind):\nctrl+'' : splits horizontally\nctrl+% : splits vertically",
"wg [up/down] [interface name found in /etc/wireguard] : controls the wireguard vpn interface",
"sudo su : enters root/admin mode",
"./filename : executes a file in your directiory. can also be used to execute files in other directories",
"lsblk : lists mounted partitions from ssds, usb drives, hard drives, and other storage mediums plugged into the device",
"mount [/dev/sd*#] [location] : mounts a partition from a storage device allowing access",
"umount [/dev/sd*#] : unmounts mounted partitions",
"[command] | grep [phrase] : sorts through the output of a command to find a phrase",
"apt [install/remove] [app name] : controls applications, programs, and other packages",
"wildcards | * - means all",
"KEYBINDS : ctrl+alt+f1-f6 will let you access and login other terminals to do other things",
"nano [filename] : opens a file in editing mode, keybinds are displayed at the bottom",
"cd [name] : changes your current directory/folder and moves you to the supplied path",
"ping [ip addr] | test connectivity to the destination device",
"mkdir [name] | creates a directory / folder with that name",
"poweroff/reboot : shutdown/turns off/restarts the computer"]

while True:
    inp = input(">>> ")
    if not inp:
        inp = " "
    if inp == "*":
        inp = " "
    print("\n\n\n")
    for item in cmd_list:
        if inp.lower() in item.lower():
            print(item)
    print("\n")