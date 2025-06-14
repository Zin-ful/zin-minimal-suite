This software is to make low-end linux devices easy and effective to use
the main issue is that the software is designed to work with itself, not to intergrate with existing software
Along with this, these programs will have varients that suite off-grid needs (communicating over LoRa)
this repo will be updated around every few weeks or so when ive made enough progress to worry about losing it

most if not all code is written in python for its memory management and networking
more advanced projects are stored elsewhere and are usually written in C

For use on CLI systems, early in dev so dont expect a ton for a bit

Currently the working curses programs are:
msg.py
main.py
uniconfig.py
zbrowse.py (not stable)
clock.py
usbctrl.py
guiweather.py

CLI only programs:
oneturnfight.py (game)
zapp.py + zget.py (app installer/srv)
zfile client + srv (file transfer service)
netdiscover
keyget + srv

the rest can be assumed to not work.

All CLI programs will be converted to curses and updated with new features
the CLI versions are just a base for the curses to build on and are usually abandoned.
However, after a program is fully completed i will end up remaking the CLI versions to match
along with this will be versions for LoRa (packet size limitations)
