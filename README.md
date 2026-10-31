<p align="center">
  <img src="https://github.com/user-attachments/assets/05bd3937-08d8-41fa-93f9-34c607a99771" width="850" alt="AyhanX Freedom Scanner banner" />
</p>

<h1 align="center">𝔸𝕪𝕙𝕒𝕟𝕏-𝔽𝕣𝕖𝕕𝕠𝕞-𝕊𝕔𝕒𝕟𝕟𝕖𝕣 🧑‍💻🌿</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20VPS-00b894?style=flat-square&logo=linux&logoColor=white" alt="Platforms" />
  <img src="https://img.shields.io/badge/Interface-Terminal-111827?style=flat-square&logo=gnubash&logoColor=00FF41" alt="Terminal" />
  <img src="https://img.shields.io/badge/Source-GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="Source code" />
</p>

<p align="center">
  <b>☁️ Cloudflare IP & Domain Scanner • 🐍 Python • 💻 Terminal UI</b><br />
  A lightweight Python tool for scanning IP ranges and domain lists, with optional proxy-link generation.
</p>

---

## 📖 Overview

**AyhanX Freedom Scanner** is a Python command-line project designed to check hosts from **Cloudflare-related IPv4 ranges and domain lists**. It downloads the lists from this repository, caches them locally, and reports hosts that respond to a ping check.

The scanner also accepts an **optional proxy configuration link template** and can generate new links by replacing the address with hosts found during a scan. It's intended for exploring and testing candidate addresses for Cloudflare-based configurations—not for guaranteeing that a particular proxy or service will work.

> **Note:** “Active” means the host responded to the tool's ping check. It does **not** confirm proxy compatibility, speed, TLS support, or successful access to a specific service. Some reachable hosts may not answer ping.

---

## ✨ Features

- 🌐 **IPv4 range scanning** — checks addresses from a downloadable range list.
- 🔎 **Domain scanning** — checks domains from the repository's domain list.
- 📡 **Ping-based checks** — displays hosts that respond.
- 📦 **Local caching** — saves downloaded lists for later runs.
- 🔢 **Adjustable scan limit** — choose how many addresses or domains to test.
- 🔗 **Optional proxy-link generation** — accepts templates for VLESS, VMess, Trojan, Shadowsocks (`ss`) and Hysteria formats.
- 📋 **Optional clipboard output** — uses a platform clipboard utility when available.
- 🎨 **Colorful terminal interface** — readable progress and summary output.
- 🐧 **Linux, VPS and Android Termux** — command-line environments supported by the project's setup instructions.

---

## 🛠 Requirements

- **Python 3**
- **Internet access** for the first list download
- **`requests`** Python package (the script attempts to install it automatically if missing)
- **`ping`** command available in your environment
- **Optional:** `xclip` on Linux to copy results to the clipboard

> On some systems, `ping` may need to be installed separately or may be restricted by network policy. A ping timeout is not proof that a host is offline.

---

## 📥 Installation

### 🐧 Linux / VPS

```bash
sudo apt update
sudo apt install python3 python3-pip curl iputils-ping
```

Download the script from its existing location in the repository:

```bash
curl -fL -o AyhanX-FredomScanner.py 'https://raw.githubusercontent.com/AyhanMansur/AyhanX-Fredom-Scanner/refs/heads/main/%F0%9D%94%B8%F0%9D%95%AA%F0%9D%95%99%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%8F-%F0%9D%94%BD%F0%9D%95%A3%F0%9D%95%96%F0%9D%95%95%F0%9D%95%A0%F0%9D%95%9E-%F0%9D%95%8A%F0%9D%95%94%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%9F%F0%9D%95%96%F0%9D%95%A3-%F0%9F%A7%91%E2%80%8D%F0%9F%92%BB%F0%9F%8C%BF/AyhanX-FredomScanner.py'
```

Run:

```bash
python3 AyhanX-FredomScanner.py
```

### 📱 Android / Termux

```bash
pkg update && pkg upgrade
pkg install python curl iputils
```

Use the same `curl -fL -o ...` command above to download the script, then run:

```bash
python AyhanX-FredomScanner.py
```

> If the automatic `requests` installation fails, install it manually with `python -m pip install requests` (or `python3 -m pip install requests` in an appropriate Python environment). Package installation rules differ between Linux distributions.

---

## 🚀 How It Works

1. **Start the script** and confirm you want to scan.
2. **Optional:** paste a supported proxy link as a template, or press Enter to skip link generation.
3. Choose **`1` for IP ranges** or **`2` for domains**.
4. The tool loads its list from a local cache or downloads it from GitHub.
5. Enter a **scan limit**, or press Enter to process the available list.
6. Review responsive hosts, the final scan summary, and any generated links.
7. Optionally copy the results to your clipboard.

```text
Do you want to start scan? [Y/n]: y
Paste your proxy link template ... (press Enter to skip)
Enter 1 for IP range scan, 2 for domain scan: 1
How many items do you want to scan? (press Enter for all): 100
Starting scan...
...
Final Summary:
  Total items scanned: 100
  Active hosts found: ...
```

*Illustrative interaction only; results depend on your network and the selected list.*

### 🔗 Proxy-link templates

The script can parse templates using the following schemes:

`vless://` · `vmess://` · `trojan://` · `ss://` · `hysteria://` · `hysteria2://`

It replaces the address field with a host found by the scanner. **Generated links are candidates, not verified working configurations.** Some formats and parameters may not be preserved perfectly; inspect any generated link before using it. Avoid sharing private credentials or complete personal configuration links in public screenshots or issues.

---

## 📁 Data Sources & Cache

- **IP ranges:** `Range.txt` in the project's existing script directory.
- **Domains:** [`domains.txt`](https://github.com/AyhanMansur/AyhanX-Fredom-Scanner/blob/main/domains.txt).
- **Local cache files:** `ranges_cache.txt` and `domains_cache.txt`, created in the directory where you run the script.

The scanner uses cached lists when they are available and nonempty. Remove the relevant cache file if you want the tool to download that list again.

---

## ⚠️ Responsible Use

Only scan networks or domains you are authorized to test, and respect service policies and rate limits. Large IP ranges can take a long time to scan because the current implementation checks hosts one at a time. This project is an independent open-source tool and is **not affiliated with Cloudflare**.

---

## 🤝 Contributing

Suggestions, bug reports and improvements are welcome through [GitHub Issues](https://github.com/AyhanMansur/AyhanX-Fredom-Scanner/issues). Please include your operating system, Python version, and a description of the issue—without exposing private proxy links or credentials.

## 📜 License

The source code is publicly available in this repository. Check the repository for a license file before assuming specific redistribution or modification permissions.

---

<div align="center">

### 📡 Connect with the Developer

<a href="https://github.com/AyhanMansur"><img src="https://img.shields.io/badge/GitHub-AyhanMansur-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://ayhanmansur.github.io/AyhanMansur/"><img src="https://img.shields.io/badge/Portfolio-Visit-333333?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Portfolio" /></a>
<a href="https://www.instagram.com/ayhan_dev.py/"><img src="https://img.shields.io/badge/Instagram-ayhan__dev.py-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram" /></a>
<a href="https://t.me/+A3DRts32ZI5mMjVk"><img src="https://img.shields.io/badge/Telegram-Join-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram" /></a>

<br /><br />

**⭐ If you find this project useful, consider starring the repository!**

Made with ❤️ by **Ayhan Mansur**

</div>
