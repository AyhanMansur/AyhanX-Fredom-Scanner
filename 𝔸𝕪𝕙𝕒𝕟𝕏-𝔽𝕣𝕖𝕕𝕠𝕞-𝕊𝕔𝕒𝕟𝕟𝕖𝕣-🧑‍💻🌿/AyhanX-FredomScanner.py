import sys
import subprocess
import random
import platform
import uuid
import urllib.parse
import os
import base64
import json
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

def ensure_requests():
    try:
        import requests
        return True
    except ImportError:
        print(f"{WARNING}⚠️ 'requests' module not found. Attempting to install using Runflare mirror...{ENDC}")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-i', 'https://mirror-pypi.runflare.com/simple', 'requests'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            import requests
            print(f"{OKGREEN}✅ 'requests' installed successfully.{ENDC}")
            return True
        except Exception as e:
            print(f"{FAIL}❌ Failed to install 'requests': {e}{ENDC}")
            return False

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

# ---------- Proxy link parsing and building ----------

def parse_proxy_link(link):
    """Parse any supported proxy link and return components dict."""
    link = link.strip()
    if not any(link.startswith(s + '://') for s in ['vless', 'vmess', 'trojan', 'ss', 'hysteria', 'hysteria2']):
        raise ValueError("Unsupported or invalid proxy link scheme.")

    if link.startswith('vless://'):
        return parse_vless(link)
    elif link.startswith('vmess://'):
        return parse_vmess(link)
    elif link.startswith('trojan://'):
        return parse_trojan(link)
    elif link.startswith('ss://'):
        return parse_shadowsocks(link)
    elif link.startswith(('hysteria://', 'hysteria2://')):
        return parse_hysteria(link)
    else:
        raise ValueError("Unsupported scheme.")

def parse_vless(link):
    # vless://uuid@host:port?params#fragment
    # We already have this, but we'll adapt to return generic structure
    # Remove scheme
    rest = link[8:]  # after vless://
    if '@' not in rest:
        raise ValueError("Invalid vless link: missing '@'")
    userinfo, rest = rest.split('@', 1)
    # userinfo is uuid
    # rest: host:port?params#fragment
    parsed = urllib.parse.urlparse('//' + rest)
    netloc = parsed.netloc
    query = parsed.query
    fragment = parsed.fragment
    if ':' in netloc:
        host, port_str = netloc.split(':', 1)
        try:
            port = int(port_str)
        except:
            port = 443
    else:
        host = netloc
        port = 443
    params = urllib.parse.parse_qs(query, keep_blank_values=True)
    # flatten values
    for k, v in params.items():
        params[k] = v[-1] if v else ''
    return {
        'scheme': 'vless',
        'userinfo': userinfo,  # uuid
        'host': host,
        'port': port,
        'params': params,
        'fragment': fragment,
        'raw': None  # for vmess we store base64
    }

def parse_vmess(link):
    # vmess://base64-encoded JSON
    b64 = link[8:]  # after vmess://
    # Add padding if needed
    b64 += '=' * (4 - len(b64) % 4)
    try:
        decoded = base64.b64decode(b64).decode('utf-8')
        data = json.loads(decoded)
    except Exception as e:
        raise ValueError(f"Invalid vmess link: {e}")
    # Extract host and port
    host = data.get('add', '')
    port = data.get('port', 443)
    # Ensure port is int
    try:
        port = int(port)
    except:
        port = 443
    # Store the entire data dict, we will modify 'add'
    return {
        'scheme': 'vmess',
        'userinfo': None,
        'host': host,
        'port': port,
        'params': {},  # not used for vmess
        'fragment': '',
        'raw': data  # store the dict
    }

def parse_trojan(link):
    # trojan://password@host:port?params#fragment
    rest = link[9:]  # after trojan://
    if '@' not in rest:
        raise ValueError("Invalid trojan link: missing '@'")
    userinfo, rest = rest.split('@', 1)
    parsed = urllib.parse.urlparse('//' + rest)
    netloc = parsed.netloc
    query = parsed.query
    fragment = parsed.fragment
    if ':' in netloc:
        host, port_str = netloc.split(':', 1)
        try:
            port = int(port_str)
        except:
            port = 443
    else:
        host = netloc
        port = 443
    params = urllib.parse.parse_qs(query, keep_blank_values=True)
    for k, v in params.items():
        params[k] = v[-1] if v else ''
    return {
        'scheme': 'trojan',
        'userinfo': userinfo,  # password
        'host': host,
        'port': port,
        'params': params,
        'fragment': fragment,
        'raw': None
    }

def parse_shadowsocks(link):
    # ss://method:password@host:port#fragment
    # or ss://base64#fragment where base64 decodes to method:password@host:port
    rest = link[5:]  # after ss://
    fragment = ''
    if '#' in rest:
        rest, fragment = rest.split('#', 1)
    # Check if rest starts with base64 (no '@' in rest) or has '@'
    if '@' in rest:
        # plain format: method:password@host:port
        userinfo, hostport = rest.split('@', 1)
        # userinfo is method:password
        method, password = userinfo.split(':', 1)
        if ':' in hostport:
            host, port_str = hostport.rsplit(':', 1)
            try:
                port = int(port_str)
            except:
                port = 443
        else:
            host = hostport
            port = 443
        # we don't have query params in plain format, but we can store as empty
        params = {}
        # reconstruct userinfo as method:password
        userinfo = f"{method}:{password}"
    else:
        # base64 format
        b64 = rest
        b64 += '=' * (4 - len(b64) % 4)
        try:
            decoded = base64.b64decode(b64).decode('utf-8')
        except:
            raise ValueError("Invalid shadowsocks base64")
        # decoded should be method:password@host:port
        if '@' not in decoded:
            raise ValueError("Invalid shadowsocks decoded string")
        userinfo, hostport = decoded.split('@', 1)
        if ':' in hostport:
            host, port_str = hostport.rsplit(':', 1)
            try:
                port = int(port_str)
            except:
                port = 443
        else:
            host = hostport
            port = 443
        params = {}
    return {
        'scheme': 'ss',
        'userinfo': userinfo,  # method:password
        'host': host,
        'port': port,
        'params': params,
        'fragment': fragment,
        'raw': None
    }

def parse_hysteria(link):
    # hysteria://host:port?params#fragment
    # or hysteria2://...
    scheme_end = link.find('://') + 3
    rest = link[scheme_end:]
    parsed = urllib.parse.urlparse('//' + rest)
    netloc = parsed.netloc
    query = parsed.query
    fragment = parsed.fragment
    if ':' in netloc:
        host, port_str = netloc.split(':', 1)
        try:
            port = int(port_str)
        except:
            port = 443
    else:
        host = netloc
        port = 443
    params = urllib.parse.parse_qs(query, keep_blank_values=True)
    for k, v in params.items():
        params[k] = v[-1] if v else ''
    return {
        'scheme': 'hysteria',
        'userinfo': None,
        'host': host,
        'port': port,
        'params': params,
        'fragment': fragment,
        'raw': None
    }

def build_proxy_link(components, new_host):
    """Rebuild the link with a new host (and same port if present)."""
    scheme = components['scheme']
    if scheme == 'vless':
        return build_vless(components, new_host)
    elif scheme == 'vmess':
        return build_vmess(components, new_host)
    elif scheme == 'trojan':
        return build_trojan(components, new_host)
    elif scheme == 'ss':
        return build_shadowsocks(components, new_host)
    elif scheme == 'hysteria':
        return build_hysteria(components, new_host)
    else:
        raise ValueError(f"Unknown scheme: {scheme}")

def build_vless(comp, new_host):
    uuid = comp['userinfo']
    port = comp['port']
    params = comp['params']
    fragment = comp['fragment']
    query_str = '&'.join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in params.items() if v)
    url = f"vless://{uuid}@{new_host}:{port}"
    if query_str:
        url += f"?{query_str}"
    if fragment:
        url += f"#{fragment}"
    return url

def build_vmess(comp, new_host):
    data = comp['raw'].copy()
    data['add'] = new_host
    # port remains
    json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    return f"vmess://{b64}"

def build_trojan(comp, new_host):
    password = comp['userinfo']
    port = comp['port']
    params = comp['params']
    fragment = comp['fragment']
    query_str = '&'.join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in params.items() if v)
    url = f"trojan://{password}@{new_host}:{port}"
    if query_str:
        url += f"?{query_str}"
    if fragment:
        url += f"#{fragment}"
    return url

def build_shadowsocks(comp, new_host):
    userinfo = comp['userinfo']  # method:password
    port = comp['port']
    fragment = comp['fragment']
    # We'll output in plain format: ss://method:password@host:port#fragment
    url = f"ss://{userinfo}@{new_host}:{port}"
    if fragment:
        url += f"#{fragment}"
    return url

def build_hysteria(comp, new_host):
    port = comp['port']
    params = comp['params']
    fragment = comp['fragment']
    query_str = '&'.join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in params.items() if v)
    url = f"hysteria://{new_host}:{port}"
    if query_str:
        url += f"?{query_str}"
    if fragment:
        url += f"#{fragment}"
    return url

# ---------- End of proxy parsing ----------

def get_cached_list(url, cache_file):
    import requests
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                content = f.read()
            items = [line.strip() for line in content.splitlines()
                     if line.strip() and not line.startswith('#')]
            if items:
                print(f"{OKGREEN}✅ Loaded {len(items)} items from local cache ({cache_file}).{ENDC}")
                return items
        except Exception as e:
            print(f"{WARNING}⚠️ Could not read cache file: {e}. Will download fresh.{ENDC}")

    print(f"{LITBU}📡 Downloading list from GitHub (this will be cached for offline use)...{ENDC}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.text
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)
        items = [line.strip() for line in content.splitlines()
                 if line.strip() and not line.startswith('#')]
        if not items:
            raise ValueError("No valid items found in the downloaded file.")
        print(f"{OKGREEN}✅ Downloaded and cached {len(items)} items to {cache_file}.{ENDC}")
        return items
    except Exception as e:
        print(f"{FAIL}❌ Failed to download or cache: {e}{ENDC}")
        sys.exit(1)

def main():
    print(BANNER)

    if not ensure_requests():
        print(f"{FAIL}❌ Cannot proceed without 'requests'. Exiting.{ENDC}")
        sys.exit(1)

    start_choice = input(f"{CYAN}❓ Do you want to start scan? [Y/n]: {ENDC}").strip().lower()
    if start_choice == 'n':
        print(f"{YELLOW}🚫 Scan cancelled by user.{ENDC}")
        sys.exit(0)

    # Ask for proxy link template
    print(f"{CYAN}✏️  Paste your proxy link template (vless, vmess, trojan, ss, hysteria).{ENDC}")
    print(f"{CYAN}   The address (IP/domain) will be replaced with each scanned host.{ENDC}")
    print(f"{CYAN}   Press Enter to skip this feature.{ENDC}")
    template = input(f"{YELLOW}➜ {ENDC}").strip()
    proxy_components = None
    if template:
        try:
            proxy_components = parse_proxy_link(template)
            print(f"{OKGREEN}✅ Template parsed successfully. Scheme: {proxy_components['scheme']}{ENDC}")
        except Exception as e:
            print(f"{WARNING}⚠️  Could not parse proxy link: {e}. Link generation will be skipped.{ENDC}")
            proxy_components = None

    scan_choice = input(f"{CYAN}❓ Enter 1 for IP range scan, 2 for domain scan: {ENDC}").strip()
    while scan_choice not in ['1', '2']:
        print(f"{WARNING}⚠️ Invalid choice. Please enter 1 or 2.{ENDC}")
        scan_choice = input(f"{CYAN}❓ Enter 1 for IP range scan, 2 for domain scan: {ENDC}").strip()

    if scan_choice == '2':
        url = "https://raw.githubusercontent.com/AyhanMansur/AyhanX-Fredom-Scanner/refs/heads/main/domains.txt"
        cache_file = "domains_cache.txt"
        item_type = "domains"
    else:
        url = "https://raw.githubusercontent.com/AyhanMansur/AyhanX-Fredom-Scanner/refs/heads/main/%F0%9D%94%B8%F0%9D%95%AA%F0%9D%95%99%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%8F-%F0%9D%94%BD%F0%9D%95%A3%F0%9D%95%96%F0%9D%95%95%F0%9D%95%A0%F0%9D%95%9E-%F0%9D%95%8A%F0%9D%95%94%F0%9D%95%92%F0%9D%95%9F%F0%9D%95%9F%F0%9D%95%96%F0%9D%95%A3-%F0%9F%A7%91%E2%80%8D%F0%9F%92%BB%F0%9F%8C%BF/Range.txt"
        cache_file = "ranges_cache.txt"
        item_type = "IP ranges"

    items = get_cached_list(url, cache_file)
    print(f"{OKGREEN}✅ Loaded {len(items)} {item_type}.{ENDC}")

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

    if scan_choice == '2':
        active, scanned = scan_domains(items, limit=scan_limit)
        all_active = active
        total_scanned = scanned
    else:
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
        print(f"{WARNING}⚠️ No active hosts found. Skipping proxy link generation.{ENDC}")

    # Generate new links if template was provided
    generated_links = []
    if proxy_components and all_active:
        print(f"\n{LITBU}📦 Generating {proxy_components['scheme']} links for each active host...{ENDC}")
        for host in all_active:
            new_link = build_proxy_link(proxy_components, host)
            generated_links.append(new_link)
            print(f"{OKGREEN}   ➜ {new_link}{ENDC}")

    # Copy options
    copy_choice = input(f"{CYAN}📋 Do you want to copy the results to clipboard? [y/N]: {ENDC}").strip().lower()
    if copy_choice in {'y', 'yes'}:
        try:
            result_text = "\n".join(generated_links) if generated_links else "\n".join(all_active)
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
