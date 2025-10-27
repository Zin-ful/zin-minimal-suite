#!/bin/sh

python3 srvmsg.py &
python3 srvmailer.py &
python3 srvstatus.py &
python3 srvstatus.py &
python3 srvreport.py &
python3 srvprogramedit.py &
python3 srv_wgkey.py &
python3 srvzget.py &
python3 srvcall.py &
python3 srvshell.py &
python3 srvstorage.py &

exec tail -f /dev/null