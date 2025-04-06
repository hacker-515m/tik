#!/bin/bash

termux-setup-storage
sleep 5

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

configure_tor() {
    torrc_path="$PREFIX/etc/tor/torrc"
    if ! grep -q "ControlPort 9051" "$torrc_path"; then
        echo -e "\n[INFO] Configuring Tor control port..."
        echo "ControlPort 9051" >> "$torrc_path"
        echo "CookieAuthentication 0" >> "$torrc_path"
    fi
}

main() {
    clear
    display_banner
    display_hacking_animation

    echo -e "\e[32m[INFO] Installing dependencies...\e[0m"
    pkg update -y && pkg upgrade -y
    pkg install -y python tor tmux
    pip install --upgrade pip
    pip install requests fake_useragent

    echo -e "\e[32m[INFO] Configuring Tor...\e[0m"
    configure_tor

    echo -e "\e[32m[INFO] Launching tool inside tmux session: \e[33mguardian_hammer\e[0m"

    tmux kill-session -t guardian_hammer 2>/dev/null

    tmux new-session -d -s guardian_hammer 'tor & sleep 5 && python start.py'

    tmux attach-session -t guardian_hammer
}

main
