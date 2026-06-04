# D0RK3R - Shodan Dork IP Extractor
# Author : https://github.com/infohlaingbwar

import argparse
import importlib
import os
import random
import re
import subprocess
import sys
import time
from urllib.parse import quote

def ensure_module(module_name, pip_name=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        pkg = pip_name or module_name
        print(f"[+] Installing '{pkg}'...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except subprocess.CalledProcessError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", pkg])
        return importlib.import_module(module_name)

requests = ensure_module("requests", "requests[socks]")

VERSION = "1.0.3"

try:
    "─".encode(sys.stdout.encoding or "utf-8")
    UNICODE = True
except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
    UNICODE = False

if UNICODE:
    T_H = "─"
    T_V = "│"
    T_TL = "┌"
    T_BL = "└"
    T_M = "├"
    T_R = "┐"
    T_BR = "┘"
    T_BAR = "═"
    T_OK = "✔"
    T_ERR = "✘"
else:
    T_H = "-"
    T_V = "|"
    T_TL = "."
    T_BL = "L"
    T_M = "|"
    T_R = "."
    T_BR = "'"
    T_BAR = "="
    T_OK = "+"
    T_ERR = "x"

C = {
    "R": "\033[91m",
    "G": "\033[92m",
    "Y": "\033[93m",
    "B": "\033[94m",
    "M": "\033[95m",
    "C": "\033[96m",
    "W": "\033[97m",
    "X": "\033[0m",
}

BANNER_ASCII = rf"""{C['R']}
  ____  _____  ____  _  ____  _____  ____
 (  _ \(  _  )(  _ \( )/ ___)(  _  )(  _ \
  )(_) ))(_)(( )(_) )|\___ \ )(_)(( )___/
 (____/(_____)(____/(_)(____/(_____)(__)
{C['X']}
{C['C']} D0RK3R - Shodan Dork IP Extractor v{VERSION}{C['X']}
{C['W']} Author : https://github.com/infohlaingbwar{C['X']}
"""

BANNER_UNICODE = rf"""{C['R']}
  ██████╗  ██████╗ ██████╗ ██╗  ██╗██████╗ ██████╗
  ╚════██╗██╔═══██╗██╔══██╗██║ ██╔╝╚════██╗██╔══██╗
   █████╔╝██║   ██║██████╔╝█████╔╝  █████╔╝██████╔╝
  ██╔═══╝ ██║   ██║██╔══██╗██╔═██╗  ╚═══██╗██╔══██╗
  ███████╗╚██████╔╝██║  ██║██║  ██╗██████╔╝██║  ██║
  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝{C['X']}
{C['C']} D0RK3R - Shodan Dork IP Extractor v{VERSION}{C['X']}
{C['W']} Author : https://github.com/infohlaingbwar{C['X']}
"""

BANNER = BANNER_UNICODE if UNICODE else BANNER_ASCII

SHODAN_FACET_URL = "https://www.shodan.io/search/facet?query={q}&facet=ip"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.2210.133",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) Version/17.2 Mobile/15E148 Safari/604.1",
]

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

PRIVATE_PREFIXES = (
    "0.", "127.", "169.254.", "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
    "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.",
    "192.168.", "10.", "224.", "240.",
)

DOTS_UNICODE = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
DOTS_ASCII = "|/-\\"
DOTS = DOTS_UNICODE if UNICODE else DOTS_ASCII


def load_proxies(path):
    proxies = []
    if not path or not os.path.isfile(path):
        return proxies
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                proxies.append(line)
    return proxies


class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.idx = 0

    def next(self):
        if not self.proxies:
            return None
        p = self.proxies[self.idx % len(self.proxies)]
        self.idx += 1
        return p


def is_private(ip):
    return ip.startswith(PRIVATE_PREFIXES)


def is_valid_ip(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def extract_ips(html):
    raw = IP_RE.findall(html)
    return [ip for ip in raw if is_valid_ip(ip) and not is_private(ip)]


def request_url(url, proxy, timeout):
    ua = random.choice(USER_AGENTS)
    headers = {"User-Agent": ua}
    proxies_dict = None
    if proxy:
        proxies_dict = {"http": proxy, "https": proxy}
    return requests.get(url, headers=headers, proxies=proxies_dict, timeout=timeout)


def truncate_proxy(p, n=40):
    return (p[:n] + "...") if len(p) > n else p


def fetch_ips(query, proxies, pages_per_proxy, max_pages, timeout, delay):
    rotator = ProxyRotator(proxies)
    all_ips = set()
    num_proxies = max(len(proxies), 1)
    total_reqs = pages_per_proxy * num_proxies
    if max_pages and max_pages < total_reqs:
        total_reqs = max_pages

    success = 0
    fails = 0
    start_ts = time.time()

    for req_num in range(1, total_reqs + 1):
        proxy = rotator.next()

        url = SHODAN_FACET_URL.format(q=quote(query))
        spinner = DOTS[req_num % len(DOTS)]
        pdisp = truncate_proxy(proxy or "direct")
        status = f"{C['Y']}{spinner}{C['X']} {C['B']}[{req_num}/{total_reqs}]{C['X']} {C['W']}{pdisp}{C['X']}  IPs: {C['G']}{len(all_ips)}{C['X']}"

        if sys.stdout.isatty():
            sys.stdout.write("\r" + " " * 80 + "\r" + status)
            sys.stdout.flush()

        try:
            resp = request_url(url, proxy, timeout)
            if resp.status_code != 200:
                fails += 1
                continue

            ips = extract_ips(resp.text)
            before = len(all_ips)
            all_ips.update(ips)
            success += 1

            if delay:
                time.sleep(delay)
        except requests.RequestException:
            fails += 1
            continue

    elapsed = time.time() - start_ts

    if sys.stdout.isatty():
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    return list(all_ips), success, fails, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="D0RK3R - Shodan Dork IP Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python d0rk3r.py -q \"port:443 country:MM\"\n"
               "  python d0rk3r.py -q \"port:80\" -p proxy.txt --pages 3\n"
               "  python d0rk3r.py -q \"nginx\" -p proxy.txt --page-max 50 -o ips.txt",
    )
    parser.add_argument("-q", "--query", required=True, help="Shodan dork query")
    parser.add_argument("-p", "--proxy", help="Proxy list file (one per line)")
    parser.add_argument("--auto-proxy", action="store_true", help="Auto-fetch proxies from GitHub")
    parser.add_argument("--pages", type=int, default=2, help="Requests per proxy (default: 2)")
    parser.add_argument("--page-max", type=int, default=0, help="Max total requests (0 = auto)")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in sec")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in sec")
    parser.add_argument("--no-banner", action="store_true", help="Skip banner")
    args = parser.parse_args()

    if not args.no_banner:
        print(BANNER)

    # Auto-fetch proxies if requested
    proxies = []
    if args.auto_proxy:
        try:
            import sys, os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, script_dir)
            from .proxy_fetcher import get_proxies
            print(f" {C['Y']}[*] Auto-fetching proxies...{C['X']}")
            proxies = get_proxies(verify=True, use_cache=True)
            if proxies:
                print(f" {C['G']}[+] Loaded {len(proxies)} working proxies{C['X']}")
            else:
                print(f" {C['R']}[!] No proxies available{C['X']}")
        except Exception as e:
            print(f" {C['R']}[!] Error: {e}{C['X']}")
    elif args.proxy:
        proxies = load_proxies(args.proxy)
    if proxies:
        print(f" {C['C']}{T_TL}{T_H}{C['X']} Proxies   : {C['G']}{len(proxies)}{C['X']}")
        total_est = len(proxies) * args.pages
        print(f" {C['C']}{T_M}{T_H}{C['X']} Requests  : {C['G']}{total_est}{C['X']} ({args.pages} per proxy)")
    else:
        print(f" {C['C']}{T_TL}{T_H}{C['X']} Proxies   : {C['Y']}none (direct){C['X']}")
    print(f" {C['C']}{T_BL}{T_H}{C['X']} Query     : {C['W']}{args.query}{C['X']}\n")

    max_pages = args.page_max if args.page_max else None

    ips, success, fails, elapsed = fetch_ips(
        query=args.query,
        proxies=proxies,
        pages_per_proxy=args.pages,
        max_pages=max_pages,
        timeout=args.timeout,
        delay=args.delay,
    )

    if not ips:
        print(f"\n {C['R']}[!] No IPs found{C['X']}")
        sys.exit(1)

    ips.sort()

    bar = f"{C['C']}{T_BAR * 48}{C['X']}"
    print(f" {bar}")
    print(f" {C['G']}{T_OK} {len(ips)} unique IPs  {C['W']}{T_V}{C['X']} {success} req OK  {C['W']}{T_V}{C['X']} {fails} fail  {C['W']}{T_V}{C['X']} {elapsed:.1f}s")
    print(f" {bar}")

    if args.output:
        with open(args.output, "w") as f:
            for ip in ips:
                f.write(ip + "\n")
        print(f" {C['G']}{T_BL}{T_H} Saved {T_R} {C['W']}{args.output}{C['X']}\n")

    for ip in ips:
        print(f" {C['G']}{T_M}{T_H}{C['X']} {ip}")

    if ips:
        print(f" {C['G']}{T_BL}{T_H}{C['X']} {C['W']}{len(ips)} total{C['X']}")


if __name__ == "__main__":
    main()
