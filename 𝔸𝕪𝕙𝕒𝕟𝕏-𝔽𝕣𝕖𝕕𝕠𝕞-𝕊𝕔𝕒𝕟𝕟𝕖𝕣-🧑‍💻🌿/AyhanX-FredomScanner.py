import sys
import subprocess
import random
import requests
import platform
import uuid
import urllib.parse
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

def scan_host(host):
    param = '-n' if sys.platform.startswith('win') else '-c'
    try:
        result = subprocess.run(['ping', param, '1', host],
                                capture_output=True, text=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def scan_network(network_str, limit=None):
    try:
        network = ip_network(network_str, strict=False)
        addresses = list(network.hosts())

        if limit is not None:
            addresses = addresses[:limit]

        color = random.choice(colors)
        print(f"{color}🔍 Scanning {network_str} ({len(addresses)} addresses)...{ENDC}")

        active_hosts = []
        for ip in addresses:
            if scan_host(str(ip)):
                active_hosts.append(str(ip))
                print(f"{OKGREEN}   ✅ {ip} is active{ENDC}")

        return active_hosts, len(addresses)
    except Exception as e:
        print(f"{FAIL}❌ Error in range {network_str}: {e}{ENDC}")
        return [], 0

def scan_domains(domain_list, limit=None):
    if limit is not None:
        domain_list = domain_list[:limit]

    color = random.choice(colors)
    print(f"{color}🔍 Scanning {len(domain_list)} domains...{ENDC}")

    active_domains = []
    for domain in domain_list:
        if scan_host(domain):
            active_domains.append(domain)
            print(f"{OKGREEN}   ✅ {domain} is active{ENDC}")

    return active_domains, len(domain_list)

def parse_vless(link):
    """Parse a vless:// link and return components."""
    # Remove leading/trailing spaces
    link = link.strip()
    if not link.startswith('vless://'):
        raise ValueError("Not a valid vless link (must start with vless://)")

    # Remove the scheme
    url = link[8:]  # remove "vless://"
    # Split at '@' to get uuid and the rest
    if '@' not in url:
        raise ValueError("Missing '@' in vless link")
    uuid_part, rest = url.split('@', 1)

    # Parse the rest as a URL: host:port?params#fragment
    # We'll use urllib.parse.urlparse on "http://" + rest to get netloc, path, params, query, fragment
    # But rest includes host, port, query, fragment
    # Prepend a dummy scheme
    parsed = urllib.parse.urlparse('//' + rest)
    netloc = parsed.netloc  # host:port
    query = parsed.query
    fragment = parsed.fragment

    # Extract host and port
    if ':' in netloc:
        host, port_str = netloc.split(':', 1)
        try:
            port = int(port_str)
        except:
            port = 443
    else:
        host = netloc
        port = 443  # default

    # Parse query string into dict
    query_dict = urllib.parse.parse_qs(query, keep_blank_values=True)
    # parse_qs gives lists, we want single values (take last if multiple)
    for k, v in query_dict.items():
        query_dict[k] = v[-1] if v else ''

    return {
        'uuid': uuid_part,
        'host': host,
        'port': port,
        'query': query_dict,
        'fragment': fragment
    }

def build_vless(components, new_host):
    """Rebuild vless link with a new host (address)."""
    uuid = components['uuid']
    port = components['port']
    query_dict = components['query'].copy()
    fragment = components['fragment']

    # Rebuild query string (sort keys for consistency)
    query_parts = []
    for key in sorted(query_dict.keys()):
        val = query_dict[key]
        if val is not None:
            query_parts.append(f"{key}={urllib.parse.quote_plus(val)}")
        else:
            query_parts.append(key)
    query_str = '&'.join(query_parts)

    # Build the new link
    if query_str:
        url = f"vless://{uuid}@{new_host}:{port}?{query_str}"
    else:
        url = f"vless://{uuid}@{new_host}:{port}"

    if fragment:
        url += f"#{fragment}"

    return url

def main():
    print(BANNER)
    start_choice = input(f"{CYAN}❓ Do you want to start scan? [Y/n]: {ENDC}").strip().lower()
    if start_choice == 'n':
        print(f"{YELLOW}🚫 Scan cancelled by user.{ENDC}")
        sys.exit(0)

    # Ask for vless template
    print(f"{CYAN}✏️  Paste your vless link template (the link whose address you want to replace).{ENDC}")
    print(f"{CYAN}   Press Enter to skip this feature.{ENDC}")
    vless_template = input(f"{YELLOW}➜ {ENDC}").strip()
    vless_components = None
    if vless_template:
        try:
            vless_components = parse_vless(vless_template)
            print(f"{OKGREEN}✅ Template parsed successfully. UUID: {vless_components['uuid']}{ENDC}")
        except Exception as e:
            print(f"{WARNING}⚠️  Could not parse vless link: {e}. Vless generation will be skipped.{ENDC}")
            vless_components = None

    scan_choice = input(f"{CYAN}❓ Enter 1 for IP range scan, 2 for domain scan: {ENDC}").strip()
    while scan_choice not in ['1', '2']:
        print(f"{WARNING}⚠️ Invalid choice. Please enter 1 or 2.{ENDC}")
        scan_choice = input(f"{CYAN}❓ Enter 1 for IP range scan, 2 for domain scan: {ENDC}").strip()

    if scan_choice == '2':
        url = "https://raw.githubusercontent.com/AyhanMansur/AyhanX-Fredom-Scanner/raw/refs/heads/main/domains.txt"
        item_type = "domains"
    else:
        url = "https://raw.githubusercontent.com/AyhanMansur/AyhanX-Fredom-Scanner/raw/refs/heads/main/%F0%9D%94%B8%F0%9D%95%AA%F0%9D%95%99%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%8F-%F0%9D%94%BD%F0%9D%95%A3%F0%9D%95%96%F0%9D%95%95%F0%9D%95%A0%F0%9D%95%9E-%F0%9D%95%8A%F0%9D%95%94%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%9F%F0%9D%95%96%F0%9D%95%A3-%F0%9F%A7%91%E2%80%8D%F0%9F%92%BB%F0%9F%8C%BF/Range.txt"
        item_type = "IP ranges"

    print(f"{LITBU}📡 Downloading {item_type} from GitHub...{ENDC}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"{FAIL}❌ Failed to download {item_type} file: {e}{ENDC}")
        sys.exit(1)

    items = [
        line.strip() for line in content.splitlines()
        if line.strip() and not line.startswith('#')
    ]

    if not items:
        print(f"{FAIL}❌ No {item_type} found in the downloaded file.{ENDC}")
        sys.exit(1)

    print(f"{OKGREEN}✅ Downloaded {len(items)} {item_type}.{ENDC}")

    limit_input = input(f"{CYAN}🔢 How many items do you want to scan? (press Enter for all): {ENDC}").strip()
    scan_limit = None
    if limit_input:
        try:
            scan_limit = int(limit_input)
            if scan_limit <= 0:
                raise ValueError
        except ValueError:
            print(f"{WARNING}⚠️ Invalid number. Scanning all items.{ENDC}")
            scan_limit = None

    print(f"{LITBU}🚀 Starting scan...{ENDC}\n")

    all_active = []
    total_scanned = 0

    if scan_choice == '2':  # domain
        active, scanned = scan_domains(items, limit=scan_limit)
        all_active = active
        total_scanned = scanned
    else:  # IP range
        remaining_limit = scan_limit
        for r in items:
            if remaining_limit is not None and remaining_limit <= 0:
                break
            active, scanned = scan_network(r, limit=remaining_limit)
            all_active.extend(active)
            total_scanned += scanned
            if remaining_limit is not None:
                remaining_limit -= scanned

    print(f"\n{BOLD}{OKGREEN}📊 Final Summary:{ENDC}")
    print(f"{CYAN}   ➤ Total items scanned: {total_scanned}{ENDC}")
    print(f"{OKGREEN}   ➤ Active hosts found: {len(all_active)}{ENDC}")

    if all_active:
        print(f"\n{YELLOW}📝 List of active {'domains' if scan_choice == '2' else 'IPs'}:{ENDC}")
        for item in all_active:
            print(f"   {OKGREEN}► {item}{ENDC}")
    else:
        print(f"{WARNING}⚠️ No active hosts found. Skipping vless generation.{ENDC}")

    # Generate vless links if template was provided and there are active hosts
    vless_links = []
    if vless_components and all_active:
        print(f"\n{LITBU}📦 Generating vless links for each active host...{ENDC}")
        for host in all_active:
            new_link = build_vless(vless_components, host)
            vless_links.append(new_link)
            print(f"{OKGREEN}   ➜ {new_link}{ENDC}")

    # Copy options
    copy_choice = input(f"{CYAN}📋 Do you want to copy the results to clipboard? [y/N]: {ENDC}").strip().lower()
    if copy_choice in {'y', 'yes'}:
        try:
            # If we have vless links, copy them; otherwise copy the active hosts list
            result_text = "\n".join(vless_links) if vless_links else "\n".join(all_active)
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
