import sys
import subprocess
import random
import requests
import platform
from ipaddress import ip_network
OKGREEN = '\033[92m'
WARNING = '\033[0;33m'
FAIL = '\033[91m'
ENDC = '\033[0m'
LITBU = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
PURPLE = '\033[95m'
BOLD = '\033[1m'
colors = [OKGREEN, LITBU, CYAN, PURPLE]
RAND_COLOR = random.choice(colors)

BANNER = f"""
{RAND_COLOR}
{OKGREEN}   █████████              █████                           █████ █████             █████████                                                             
  ███▒▒▒▒▒███            ▒▒███                           ▒▒███ ▒▒███             ███▒▒▒▒▒███                                                            
 ▒███    ▒███  █████ ████ ▒███████    ██████   ████████   ▒▒███ ███             ▒███    ▒▒▒   ██████   ██████   ████████   ████████    ██████  ████████ 
 ▒███████████ ▒▒███ ▒███  ▒███▒▒███  ▒▒▒▒▒███ ▒▒███▒▒███   ▒▒█████    ██████████▒▒█████████  ███▒▒███ ▒▒▒▒▒███ ▒▒███▒▒███ ▒▒███▒▒███  ███▒▒███▒▒███▒▒███
 ▒███▒▒▒▒▒███  ▒███ ▒███    ▒███ ▒███   ███████  ▒███ ▒███    ███▒███  ▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒███▒███ ▒▒▒   ███████  ▒███ ▒███  ▒███ ▒███ ▒███████  ▒███ ▒▒▒ 
 ▒███    ▒███  ▒███ ▒███  ▒███ ▒███  ███▒▒███  ▒███ ▒███   ███ ▒▒███             ███    ▒███▒███  ███ ███▒▒███  ▒███ ▒███  ▒███ ▒███ ▒███▒▒▒   ▒███     
 █████   █████ ▒▒███████  ████ █████▒▒████████ ████ █████ █████ █████           ▒▒█████████ ▒▒██████ ▒▒████████ ████ █████ ████ █████▒▒██████  █████    
▒▒▒▒▒   ▒▒▒▒▒   ▒▒▒▒▒███ ▒▒▒▒ ▒▒▒▒▒  ▒▒▒▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒ ▒▒▒▒▒ ▒▒▒▒▒             ▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒▒   ▒▒▒▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒     
                ███ ▒███                                                                                                                                
               ▒▒██████                                                                                                                                 
                ▒▒▒▒▒▒                                                                                                                                  
"""
def scan_host(ip):
    param = '-n' if sys.platform.startswith('win') else '-c'
    try:
        result = subprocess.run(['ping', param, '1', str(ip)],
                                capture_output=True, text=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def scan_network(network_str, limit=None):
    """اسکن یک محدوده با محدودیت اختیاری"""
    try:
        network = ip_network(network_str, strict=False)
        addresses = list(network.hosts())

        if limit is not None:
            addresses = addresses[:limit]

        color = random.choice(colors)
        print(f"{color}🔍 Scanning {network_str} ({len(addresses)} addresses)...{ENDC}")

        active_hosts = []
        for ip in addresses:
            if scan_host(ip):
                active_hosts.append(str(ip))
                print(f"{OKGREEN}   ✅ {ip} is active{ENDC}")

        return active_hosts, len(addresses)
    except Exception as e:
        print(f"{FAIL}❌ Error in range {network_str}: {e}{ENDC}")
        return [], 0
def main():
    print(BANNER)
    start_choice = input(f"{CYAN}❓ Do you want to start scan? [Y/n]: {ENDC}").strip().lower()
    if start_choice == 'n':
        print(f"{YELLOW}🚫 Scan cancelled by user.{ENDC}")
        sys.exit(0)
    url = "https://raw.githubusercontent.com/AyhanMansur/AyhanX-Fredom-Scanner/refs/heads/main/%F0%9D%94%B8%F0%9D%95%AA%F0%9D%95%99%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%8F-%F0%9D%94%BD%F0%9D%95%A3%F0%9D%95%96%F0%9D%95%95%F0%9D%95%A0%F0%9D%95%9E-%F0%9D%95%8A%F0%9D%95%94%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%9F%F0%9D%95%96%F0%9D%95%A3-%F0%9F%A7%91%E2%80%8D%F0%9F%92%BB%F0%9F%8C%BF/Range.txt"

    print(f"{LITBU}📡 𝔸𝕪𝕙𝕒𝕟𝕏-𝔽𝕣𝕖𝕕𝕠𝕞-𝕊𝕔𝕒𝕟𝕟𝕖𝕣-🧑‍💻🌿 Downloading range list from GitHub...{ENDC}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"{FAIL}❌ Failed to download ranges.txt: {e}{ENDC}")
        sys.exit(1)

    ranges = [
        line.strip() for line in content.splitlines()
        if line.strip() and not line.startswith('#')
    ]

    if not ranges:
        print(f"{FAIL}❌ No IP ranges found in the downloaded file.{ENDC}")
        sys.exit(1)

    print(f"{OKGREEN}✅ Downloaded {len(ranges)} IP ranges.{ENDC}")

    limit_input = input(f"{CYAN}🔢 How many IPs do you want to scan? (press Enter for all): {ENDC}").strip()
    scan_limit = None
    if limit_input:
        try:
            scan_limit = int(limit_input)
            if scan_limit <= 0:
                raise ValueError
        except ValueError:
            print(f"{WARNING}⚠️ Invalid number. Scanning all IPs.{ENDC}")
            scan_limit = None

    print(f"{LITBU}🚀 Starting scan...{ENDC}\n")

    all_active = []
    scanned_so_far = 0
    processed_ranges = 0
    remaining_limit = scan_limit

    for r in ranges:
        if remaining_limit is not None and remaining_limit <= 0:
            break

        processed_ranges += 1
        active, scanned = scan_network(r, limit=remaining_limit)
        all_active.extend(active)
        scanned_so_far += scanned
        if remaining_limit is not None:
            remaining_limit -= scanned

    print(f"\n{BOLD}{OKGREEN}📊 Final Summary:{ENDC}")
    print(f"{CYAN}   ➤ IP ranges processed: {processed_ranges}{ENDC}")
    print(f"{CYAN}   ➤ Addresses scanned: {scanned_so_far}{ENDC}")
    print(f"{OKGREEN}   ➤ Active hosts found: {len(all_active)}{ENDC}")
    if all_active:
        print(f"\n{YELLOW}📝 List of active IPs:{ENDC}")
        for ip in all_active:
            print(f"   {OKGREEN}► {ip}{ENDC}")

    copy_choice = input(f"{CYAN}📋 Do you want to copy the results to clipboard? [y/N]: {ENDC}").strip().lower()
    if copy_choice in {'y', 'yes'}:
        try:
            result_text = "\n".join(all_active)
            if platform.system() == "Windows":
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(result_text)
                win32clipboard.CloseClipboard()
            elif platform.system() == "Linux":
                subprocess.run(['xclip', '-selection', 'clipboard'], input=result_text, text=True, check=False)
            elif platform.system() == "Darwin":
                subprocess.run(['pbcopy'], input=result_text, text=True, check=False)
            print(f"{OKGREEN}✅ Results copied to clipboard.{ENDC}")
        except Exception as e:
            print(f"{WARNING}⚠️ Could not copy results: {e}{ENDC}")

if __name__ == "__main__":
    main()
