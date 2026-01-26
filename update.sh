#!/bin/sh
echo "make sure to run as root/sudo"
echo "updating only graphical tools"
sleep 1
cd ~/
echo "removing old files"
sleep 1
rm -rf zin-minimal-suite
git clone https://github.com/Zin-ful/zin-minimal-suite
echo " "
echo "copying files to /usr/local/bin"
sleep 1
cp ~/zin-minimal-suite/graphics/connection/guimsg.py /usr/local/bin/msg
cp ~/zin-minimal-suite/graphics/sys-tools/guibatttest.py /usr/local/bin/batterytest
cp ~/zin-minimal-suite/graphics/sys-tools/guiusbctrl.py /usr/local/bin/usbctrl
cp ~/zin-minimal-suite/graphics/sys-tools/guizbrowse.py /usr/local/bin/browser
cp ~/zin-minimal-suite/graphics/sys-tools/guiztemp.py /usr/local/bin/temp
cp ~/zin-minimal-suite/graphics/tools/guiweather.py /usr/local/bin/weather
cp ~/zin-minimal-suite/graphics/tools/guiwgkey.py /usr/local/bin/wgmgr
cp ~/zin-minimal-suite/graphics/tools/guiclock.py /usr/local/bin/clock

cp ~/zin-minimal-suite/connection/msg.py /usr/local/bin/msg-cli
cp ~/zin-minimal-suite/tools/wgkey.py /usr/local/bin/wgmgr-cli
cp ~/zin-minimal-suite/tools/mailer.py /usr/local/bin/mailer-cli
cp ~/zin-minimal-suite/tools/transfer.py /usr/local/bin/transfer-cli

cd ~/zin-minimal-suite/sys-tools/benchmarks
make
cp ~/zin-minimal-suite/sys-tools/benchmarks/zintest /usr/local/bin/zintest

echo "marking files as executable"
sleep 1

chmod +x /usr/local/bin/zintest

chmod +x /usr/local/bin/msg-cli
chmod +x /usr/local/bin/wgmgr-cli
chmod +x /usr/local/bin/mailer-cli
chmod +x /usr/local/bin/transfer-cli

chmod +x /usr/local/bin/msg
chmod +x /usr/local/bin/batterytest
chmod +x /usr/local/bin/usbctrl
chmod +x /usr/local/bin/browser
chmod +x /usr/local/bin/temp
chmod +x /usr/local/bin/weather
chmod +x /usr/local/bin/wgmgr
chmod +x /usr/local/bin/clock

echo "purging directory"
sleep 1
#rm -rf zin-minimal-suite


echo "New commands:"

echo "msg-cli"
echo "wgmgr-cli"
echo "mailer-cli"
echo "transfer-cli"
echo "zintest"
echo "msg"
echo "batterytest"
echo "usbctrl"
echo "browser"
echo "temp"
echo "weather"
echo "wgmgr"
echo "clock"
