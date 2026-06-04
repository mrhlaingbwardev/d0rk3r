#!/usr/bin/env python3
# Proxy Auto-Fetcher for D0RK3R
# Fetches fresh proxies from GitHub public lists

import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
]

CACHE_FILE = ".proxy_cache.txt"
CACHE_TTL = 3600 * 6  # 6 hours


def fetch_proxies_from_url(url, timeout=10):
    """Download proxy list from URL"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            lines = resp.text.strip().split('\n')
            proxies = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Detect protocol
                    if '://' not in line:
                        # Guess based on source URL
                        if 'socks5' in url.lower():
                            line = 'socks5://' + line
                        elif 'socks4' in url.lower():
                            line = 'socks4://' + line
                        else:
                            line = 'http://' + line
                    proxies.append(line)
            return proxies
    except Exception:
        pass
    return []


def fetch_all_proxies(sources=PROXY_SOURCES, max_workers=5):
    """Fetch proxies from multiple sources concurrently"""
    all_proxies = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_proxies_from_url, url): url for url in sources}
        
        for future in as_completed(futures):
            proxies = future.result()
            all_proxies.extend(proxies)
    
    # Deduplicate
    return list(set(all_proxies))


def test_proxy(proxy, test_url="http://www.google.com", timeout=5):
    """Test if proxy is working"""
    try:
        proxies_dict = {"http": proxy, "https": proxy}
        resp = requests.get(test_url, proxies=proxies_dict, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def verify_proxies(proxies, max_workers=20, max_test=100):
    """Verify proxies concurrently (test sample)"""
    # Test only a sample to save time
    sample = proxies[:max_test] if len(proxies) > max_test else proxies
    working = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_proxy, proxy): proxy for proxy in sample}
        
        for future in as_completed(futures):
            proxy = futures[future]
            if future.result():
                working.append(proxy)
    
    return working


def load_cached_proxies():
    """Load proxies from cache if fresh"""
    if not os.path.exists(CACHE_FILE):
        return None
    
    # Check cache age
    mtime = os.path.getmtime(CACHE_FILE)
    age = time.time() - mtime
    
    if age > CACHE_TTL:
        return None
    
    with open(CACHE_FILE, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    
    return proxies if proxies else None


def save_to_cache(proxies):
    """Save proxies to cache file"""
    with open(CACHE_FILE, 'w') as f:
        for proxy in proxies:
            f.write(proxy + '\n')


def get_proxies(verify=True, use_cache=True):
    """Main function: get working proxies"""
    # Try cache first
    if use_cache:
        cached = load_cached_proxies()
        if cached:
            return cached
    
    # Fetch from sources
    proxies = fetch_all_proxies()
    
    if not proxies:
        return []
    
    # Optionally verify
    if verify:
        proxies = verify_proxies(proxies)
    
    # Save to cache
    if proxies:
        save_to_cache(proxies)
    
    return proxies


if __name__ == "__main__":
    print("[*] Fetching proxies from GitHub sources...")
    proxies = fetch_all_proxies()
    print(f"[+] Fetched {len(proxies)} proxies")
    
    print("[*] Verifying proxies (testing sample of 50)...")
    working = verify_proxies(proxies, max_test=50)
    print(f"[+] {len(working)} working proxies")
    
    if working:
        save_to_cache(working)
        print(f"[+] Saved to {CACHE_FILE}")
        for p in working[:10]:
            print(f"    {p}")
