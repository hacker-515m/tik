#!/bin/bash

termux-setup-storage
sleep 10

clear

display_banner() {

    clear
    echo -e "\e[32m"
    echo "  __     ______  _____  _____  _____  _   _ "
    echo "  \ \   / / __ \|  __ \|  __ \|  __ \| \ | |"
    echo "   \ \_/ / |  | | |__) | |__) | |  | |  \| |"
    echo "    \   /| |  | |  _  /|  _  /| |  | |     |"
    echo "     | | | |__| | | \ \| | \ \| |__| | |\  |"
    echo "     |_|  \____/|_|  \_\_|  \_\_____/|_| \_|"
    echo -e "\e[0m"
    sleep 2
}

display_hacking_animation() {
    for i in {1..10}; do
        echo -e "\e[31m[+] Initiating cyber attack protocols... \e[0m"
        sleep 0.3
        echo -e "\e[34m[+] Bypassing security layers... \e[0m"
        sleep 0.3
        echo -e "\e[33m[+] Deploying AI-driven assault... \e[0m"
        sleep 0.3
    done
    sleep 2
    clear
}

# Start installation
clear
display_banner
display_hacking_animation

# Update and install dependencies
echo -e "\e[32m[INFO] Updating system and installing dependencies...\e[0m"
pkg update -y && pkg upgrade -y
pkg install -y python tor
pip install --upgrade pip
pip install requests fake_useragent concurrent.futures

# Start Tor service
echo -e "\e[32m[INFO] Starting Tor service...\e[0m"
tor &
sleep 5

# Launching the main script
echo -e "\e[32m[INFO] Running TikTok Guardian Hammer...\e[0m"
python start.py
