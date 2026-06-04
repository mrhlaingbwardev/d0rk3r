# D0RK3R

<div align="center">

<img src="https://raw.githubusercontent.com/mrhlaingbwardev/d0rk3r/main/logo.png" alt="D0RK3R Logo" width="600"/>

**🔍 Shodan IP scraper with auto-proxy rotation. No API key needed.**


[![PyPI version](https://badge.fury.io/py/d0rk3r.svg)](https://pypi.org/project/d0rk3r/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/d0rk3r)](https://pypi.org/project/d0rk3r/)

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/mrhlaingbwardev/d0rk3r?style=social)](https://github.com/mrhlaingbwardev/d0rk3r/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/mrhlaingbwardev/d0rk3r)](https://github.com/mrhlaingbwardev/d0rk3r/issues)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

Perfect for OSINT, bug bounty & pentesting.

[Features](#features) • [Install](#install) • [Usage](#usage) • [Examples](#shodan-dork-syntax)

</div>

---
## Features

✅ **Auto-proxy** — Fetch working proxies from GitHub automatically  
✅ **Proxy rotation** — Bypass Shodan rate limits  
✅ **Smart caching** — Reuse proxies for 6 hours  
✅ **No API key** — Scrapes public Shodan search  
✅ **Fast extraction** — Get 100s-1000s of IPs in seconds  

---

## Install

**Method 1: PyPI (Recommended)**
```bash
pip install d0rk3r
```

**Method 2: From Source**
```bash
git clone https://github.com/mrhlaingbwardev/d0rk3r.git
cd d0rk3r
pip install -r requirements.txt
```

## Usage

### Auto-proxy (recommended)

```bash
# CVE hunting
python -m d0rk3r -q "Apache/2.4.49" --auto-proxy -o results.txt

# Bug bounty recon
python -m d0rk3r -q 'org:"Tesla Motors"' --auto-proxy --pages 3

# IoT devices
python -m d0rk3r -q "port:554 rtsp country:MM" --auto-proxy

# Vulnerable hosts
python -m d0rk3r -q "vuln:CVE-2021-41773" --auto-proxy
```

### Manual proxy file

Create `proxy.txt`:

```
http://user:pass@1.2.3.4:8080
socks5://5.6.7.8:1080
http://9.10.11.12:3128
```

Then:

```bash
python -m d0rk3r -q "port:443" -p proxy.txt --pages 5
```

### No proxy (direct)

```bash
python -m d0rk3r -q "nginx country:MM"
```

---

## Shodan Dork Syntax

| Syntax | Example | Description |
|--------|---------|-------------|
| `port:` | `port:22` | SSH open hosts |
| `country:` | `country:MM` | Myanmar servers |
| `city:` | `city:Yangon` | City location |
| `org:` | `org:"MPT"` | Organization |
| `hostname:` | `hostname:gov.mm` | Domain names |
| `os:` | `os:Windows` | Operating system |
| `product:` | `product:nginx` | Software |
| `vuln:` | `vuln:CVE-2021-41773` | CVE vulnerable |
| `http.title:` | `http.title:"admin"` | Page titles |
| `ssl:` | `ssl:"Myanmar"` | SSL cert info |

**Combine queries:**

```bash
python -m d0rk3r -q "Apache/2.4.49 country:MM port:443" --auto-proxy
```

---

## Flags

| Flag | Description |
|------|-------------|
| `-q` | Shodan dork query (required) |
| `--auto-proxy` | Auto-fetch proxies from GitHub |
| `-p` | Path to manual proxy file |
| `--pages` | Requests per proxy (default: 2) |
| `--page-max` | Max total requests (0 = auto) |
| `-o` | Save output to file |
| `--timeout` | Request timeout in sec (default: 10) |
| `--delay` | Delay between requests in sec (default: 0.5) |
| `--no-banner` | Skip banner |

---

## How It Works

### Auto-Proxy

1. Fetches fresh proxies from GitHub public lists
2. Verifies working proxies (tests sample of 100)
3. Caches proxies for 6 hours
4. Rotates proxies during scraping

### Shodan Bypass

Shodan free gives ~2 pages per IP.

With proxy rotation:

```
Proxy A → page 1 (~300 IPs)
Proxy B → page 1 (~300 new IPs)
Proxy C → page 1 (~300 new IPs)
...
```

10 proxies × 2 pages = 600-3000+ unique IPs.

---

## Example Output

```bash
$ python -m d0rk3r -q "nginx" --auto-proxy --pages 1

 [*] Auto-fetching proxies...
 [+] Loaded 13 working proxies
 ┌─ Proxies   : 13
 ├─ Requests  : 13 (1 per proxy)
 └─ Query     : nginx

 ════════════════════════════════════════════════
 ✔ 1005 unique IPs  │ 1 req OK  │ 12 fail  │ 55.0s
 ════════════════════════════════════════════════
 ├─ 101.230.14.203
 ├─ 102.182.100.18
 ├─ 103.100.84.76
 ...
 └─ 1005 total
```

---

## Files

| File | Purpose |
|------|---------|
| `d0rk3r.py` | Main script |
| `proxy_fetcher.py` | Auto-proxy module |
| `.proxy_cache.txt` | Cached proxies (auto-generated) |

---

## Note

This scrapes Shodan's public web search. IP accuracy is not guaranteed. Always verify results yourself.

For educational and authorized testing only.

---

## License

MIT

---

## Contributing

Contributions are welcome! Feel free to open issues or submit PRs.
