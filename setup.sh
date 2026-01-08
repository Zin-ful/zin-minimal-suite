#!/bin/sh

cd ~/

export USER=$(whoami)

echo "python3 .zinapp/autorun/main.py" >> .bashrc

rm -rf .zinapp/homescreen/apps.conf

mkdir .zinapp
mkdir .zinapp/autorun
cp zin-minimal-suite/graphics/tools/guiwgkey.py .zinapp/autorun
cp zin-minimal-suite/graphics/connection/guimsg.py .zinapp/autorun
cp zin-minimal-suite/graphics/tools/guiweather.py .zinapp/autorun
cp zin-minimal-suite/main.py .zinapp/autorun
cp zin-minimal-suite/graphics/sys-tools/guiusbctrl.py .zinapp/autorun
cp zin-minimal-suite/graphics/sys-tools/guiztemp.py .zinapp/autorun
cp zin-minimal-suite/graphics/tools/guiclock.py .zinapp/autorun

mkdir .zinapp/homescreen

echo "/home/$USER/.zinapp/autorun/guimsg.py:Messenger" >> ".zinapp/homescreen/apps.conf"
echo "/home/$USER/.zinapp/autorun/guiweather.py:Weather" >> ".zinapp/homescreen/apps.conf"
echo "/home/$USER/.zinapp/autorun/guiwgkey.py:Wireguard Manager" >> ".zinapp/homescreen/apps.conf"
echo "/home/$USER/.zinapp/autorun/guiclock.py:Clock" >> ".zinapp/homescreen/apps.conf"
echo "/home/$USER/.zinapp/autorun/guiztemp.py:Temperature" >> ".zinapp/homescreen/apps.conf"
echo "/home/$USER/.zinapp/autorun/guiusbctrl.py:USB Control" >> ".zinapp/homescreen/apps.conf"
