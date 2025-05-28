very early in developement

Working:
Weather tool + GUI, Linux & background service
Emergency Updater
Messenger + Server
Network Discovery
zget + server

Partially working:
File browser
uniconfig

Not working:
Phone
Phone server
Universal Helper Tool
Zpush

notes cause I'm dumb:
in wg0, use /24 in your interface and /32 on peers so you don't communicate with ips outside the peers range

client should always be /24 because we want the full range of the network to communicate with

/32 is when we only want to communicate with one device like a server to peers or client to client (p2p)
