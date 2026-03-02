#!/bin/sh

echo "1.  | 1.7.10 Classic|"
echo "2.  | 1.7.10 Forge  |"
echo "3.  | 1.12.2 Paper  |"
echo "4.  | 1.12.2 Forge  |"
echo "5.  | 1.16.5 Paper  |"
echo "6.  | 1.16.5 Forge  |"
echo "7.  | 1.20.1 Paper  |"
echo "8.  | 1.20.1 Folia  |"
echo "9.  | 1.20.1 Forge  |"
echo "10. | 1.21.11 Paper |"
echo "11. | 1.21.11 Folia |"

echo ""
echo "Install which server?"
read -p ">>> " server

# --- Distro detection ---
if command -v pacman > /dev/null 2>&1; then
    DISTRO="arch"
elif command -v apt > /dev/null 2>&1; then
    DISTRO="debian"
else
    echo "Unsupported distro: neither pacman nor apt found."
    exit 1
fi

echo "Detected distro: $DISTRO"

# --- Java install function ---
# Usage: install_java <version>   (e.g. 8, 17, 21)
install_java() {
    ver=$1
    if [ "$DISTRO" = "arch" ]; then
        case $ver in
            8)  sudo pacman -S --needed --noconfirm jdk8-openjdk ;;
            17) sudo pacman -S --needed --noconfirm jdk17-openjdk ;;
            21) sudo pacman -S --needed --noconfirm jdk21-openjdk ;;
            *)  echo "Unknown java version $ver"; exit 1 ;;
        esac
    else
        # Debian/Ubuntu — set up Adoptium repo if needed
        sudo apt install -y gnupg
        check=$(ls /usr/share/keyrings/ | grep adopt)
        case "$check" in
            *adoptium*)
                echo "------GPG Already exists-------"
                sleep 1
                ;;
            *)
                wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | sudo gpg --dearmor -o /usr/share/keyrings/adoptium.gpg
                echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/adoptium.list
                sudo apt update
                ;;
        esac
        sudo apt purge temurin-*-jdk -y
        sudo apt install -y "temurin-${ver}-jdk"
    fi
}

mkdir -p server
cd server

case $server in
  1)
    LINK="https://piston-data.mojang.com/v1/objects/952438ac4e01b4d115c5fc38f891710c4941df29/server.jar"
    install_java 8
    properties="#Minecraft server properties
generator-settings=
op-permission-level=4
allow-nether=true
level-name=world
enable-query=false
allow-flight=false
announce-player-achievements=true
server-port=25565
level-type=DEFAULT
enable-rcon=false
level-seed=
force-gamemode=false
server-ip=
max-build-height=256
spawn-npcs=true
white-list=false
spawn-animals=true
hardcore=false
snooper-enabled=true
online-mode=false
resource-pack=
pvp=true
difficulty=1
enable-command-block=false
gamemode=0
player-idle-timeout=0
max-players=20
spawn-monsters=true
generate-structures=true
view-distance=10
motd=Zinful's Server"
    ;;
  2)
    LINK="https://maven.minecraftforge.net/net/minecraftforge/forge/1.7.10-10.13.4.1614-1.7.10/forge-1.7.10-10.13.4.1614-1.7.10-installer.jar"
    install_java 8
    properties=""
    ;;
  3)
    LINK="https://fill-data.papermc.io/v1/objects/3a2041807f492dcdc34ebb324a287414946e3e05ec3df6fd03f5b5f7d9afc210/paper-1.12.2-1620.jar"
    echo "-XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32" > user_jvm_args.txt
    install_java 8
    properties=""
    ;;
  4)
    LINK="https://maven.minecraftforge.net/net/minecraftforge/forge/1.12.2-14.23.5.2859/forge-1.12.2-14.23.5.2859-installer.jar"
    echo "" > user_jvm_args.txt
    install_java 8
    properties="#Minecraft server properties
max-tick-time=60000
generator-settings=
force-gamemode=false
allow-nether=true
gamemode=0
enable-query=false
player-idle-timeout=0
difficulty=1
spawn-monsters=true
op-permission-level=4
pvp=true
snooper-enabled=true
level-type=DEFAULT
hardcore=false
enable-command-block=false
max-players=4
network-compression-threshold=256
resource-pack-sha1=
max-world-size=29999984
server-port=25565
server-ip=
spawn-npcs=true
allow-flight=false
level-name=world
view-distance=10
resource-pack=
spawn-animals=true
white-list=false
generate-structures=true
online-mode=false
max-build-height=256
level-seed=
prevent-proxy-connections=false
use-native-transport=true
enable-rcon=false
motd=Zinful's Server"
    ;;
  5)
    LINK="https://fill-data.papermc.io/v1/objects/e67da4851d08cde378ab2b89be58849238c303351ed2482181a99c2c2b489276/paper-1.16.5-794.jar"
    echo "-XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32" > user_jvm_args.txt
    install_java 8
    properties=""
    ;;
  6)
    LINK="https://maven.minecraftforge.net/net/minecraftforge/forge/1.16.5-36.2.34/forge-1.16.5-36.2.34-installer.jar"
    echo "-XX:+UseZGC" > user_jvm_args.txt
    install_java 8
    properties=""
    ;;
  7)
    LINK="https://fill-data.papermc.io/v1/objects/67f31f691afd52a0c4ce33827fd635d0d0e86d46dec0ef6f89e1d58cd27832cf/paper-1.20.1-196-mojang.jar"
    echo "-XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32" > user_jvm_args.txt
    install_java 17
    properties=""
    ;;
  8)
    LINK="https://fill-data.papermc.io/v1/objects/e553e1a535a91aa28c543730f1a3db62f3c51b0df3f193a7732658b1f22d74be/folia-1.20.1-17-mojang.jar"
    echo "-XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32" > user_jvm_args.txt
    install_java 17
    properties=""
    ;;
  9)
    LINK="https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.4.10/forge-1.20.1-47.4.10-installer.jar"
    echo "-XX:+UseZGC" > user_jvm_args.txt
    install_java 17
    properties="allow-flight=false
allow-nether=true
broadcast-console-to-ops=true
broadcast-rcon-to-ops=true
difficulty=normal
enable-command-block=false
enable-jmx-monitoring=false
enable-query=false
enable-rcon=false
enable-status=true
enforce-secure-profile=true
enforce-whitelist=false
entity-broadcast-range-percentage=100
force-gamemode=false
function-permission-level=2
gamemode=survival
generate-structures=true
generator-settings={}
hardcore=false
hide-online-players=false
initial-disabled-packs=
initial-enabled-packs=vanilla
level-name=world
level-seed=
level-type=minecraft\:normal
max-chained-neighbor-updates=1000000
max-players=20
max-tick-time=60000
max-world-size=29999984
motd=Zinful's Server
network-compression-threshold=256
online-mode=false
op-permission-level=4
player-idle-timeout=0
prevent-proxy-connections=false
pvp=true
query.port=25565
rate-limit=0
rcon.password=
rcon.port=25575
require-resource-pack=false
resource-pack=
resource-pack-prompt=
resource-pack-sha1=
server-ip=
server-port=25565
simulation-distance=6
spawn-animals=true
spawn-monsters=true
spawn-npcs=true
spawn-protection=16
sync-chunk-writes=true
text-filtering-config=
use-native-transport=true
view-distance=10
white-list=false"
    ;;
  10)
    LINK="https://fill-data.papermc.io/v1/objects/367f5088c7cc5c8f83cbededf4760622d4a27425be45611d3db6f11c75fac901/paper-1.21.11-126.jar"
    echo "-XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32" > user_jvm_args.txt
    install_java 21
    properties=""
    ;;
  11)
    LINK="https://fill-data.papermc.io/v1/objects/f52c408490a0225611e67907a3ca19f7e6da2c6bc899e715d5f46844e7103c39/folia-1.21.11-14.jar"
    echo "-XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32" > user_jvm_args.txt
    install_java 21
    properties=""
    ;;
  *)
    echo "no"
    exit 1
    ;;
esac

wget "$LINK"
file=$(ls | grep jar)

case "$file" in
  *forge*)
    java -Djava.awt.headless=true -jar "$file" --installServer
    rm "$file"
    rm -f "$file.log"
    name=$(ls | grep -i "forge.*jar" | grep -v installer)
    ;;
  *)
    name="$file"
    ;;
esac

echo "eula=true" > eula.txt
echo "$properties" > server.properties
echo "java -Djava.awt.headless=true -jar $name" > run
chmod +x run