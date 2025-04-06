#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Guardian Hammer v4.2 - Termux Fixed Version
"""

import os
import subprocess
import time
import socket
import hashlib
import random
import requests
import sys
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from fake_useragent import UserAgent

# ===== Global Configuration =====
CONFIG = {
    "tor_socks": "socks5://127.0.0.1:9050",  # Changed to socks5
    "max_threads": 20,
    "requests_per_round": 10,
    "control_port": 9051,
    "control_password": "mySecur3!Pass",
    "torrc_path": "/data/data/com.termux/files/usr/etc/tor/torrc",
    "ip_check_url": "https://api.ipify.org",
    "max_retries": 3,
    "tor_timeout": 120,
    "tor_connection_retries": 5,
    "newnym_wait": 7
}

# ===== Global State =====
current_ip = None
ip_lock = Lock()
tor_process = None

def signal_handler(sig, frame):
    print("\n[!] Received shutdown signal. Cleaning up...")
    if tor_process:
        tor_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def install_dependencies():
    """Install required packages and Python modules"""
    print("[+] Installing dependencies...")
    subprocess.run(["pkg", "install", "-y", "tor", "python"], check=True)
    subprocess.run(["pip", "install", "--upgrade", "requests", "pysocks", "fake-useragent"], check=True)

def kill_existing_tor():
    try:
        subprocess.run(["pkill", "-f", "tor"], check=True)
        time.sleep(1)
        print("[+] Killed existing Tor processes")
    except subprocess.CalledProcessError:
        pass

def setup_torrc():
    tor_dir = os.path.dirname(CONFIG["torrc_path"])
    os.makedirs(tor_dir, exist_ok=True)
    
    torrc_content = f"""
ControlPort {CONFIG["control_port"]}
HashedControlPassword {generate_hashed_password(CONFIG["control_password"])}
SocksPort 9050
DataDirectory {tor_dir}/data
Log notice file {tor_dir}/notice.log
""".strip()
    
    with open(CONFIG["torrc_path"], "w") as f:
        f.write(torrc_content)
    print(f"[+] Torrc configured at {CONFIG['torrc_path']}")

def generate_hashed_password(password: str):
    result = subprocess.run(
        ["tor", "--hash-password", password],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().splitlines()[-1]

def start_tor_service():
    global tor_process
    kill_existing_tor()
    
    print("[+] Starting Tor service...")
    tor_process = subprocess.Popen(
        ["tor", "-f", CONFIG["torrc_path"]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if not verify_tor_connection():
        print("[!] Tor failed to start. Performing full setup...")
        install_dependencies()
        setup_torrc()
        start_tor_service()

def verify_tor_connection():
    for _ in range(CONFIG["tor_connection_retries"]):
        try:
            session = requests.Session()
            session.proxies = {
                'http': CONFIG["tor_socks"],
                'https': CONFIG["tor_socks"]
            }
            response = session.get(CONFIG["ip_check_url"], timeout=10)
            
            with ip_lock:
                global current_ip
                if current_ip != response.text:
                    print(f"[+] Tor IP: {response.text}")
                    current_ip = response.text
                    return True
        except Exception as e:
            print(f"[!] Tor check failed: {str(e)}")
            time.sleep(2)
    return False

# باقي الدوال تبقى كما هي في الإصدار السابق...

if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        sys.exit("[!] Linux/Android only!")
    
    install_dependencies()
    target = input("[?] Enter target username: ").strip('@')
    print(f"[*] Targeting: @{target}")
    
    setup_torrc()
    start_tor_service()
    launch_continuous_attack(target)
