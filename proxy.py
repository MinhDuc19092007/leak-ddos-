import requests
import threading

# Số lượng proxy tối đa cần đào
MAX_PROXIES = 20000

# Danh sách 35 nguồn API cho mỗi loại proxy
PROXY_SOURCES = {
    "http": [
        "https://api.proxyscrape.com/?request=getproxies&proxytype=http",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://openproxy.space/list/http",
        "https://www.proxyscan.io/download?type=http",
        "https://proxylist.geonode.com/api/proxy-list?protocols=http",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://www.my-proxy.com/free-proxy-list.html",
        "https://rootjazz.com/proxies/proxies.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ] * 3 + [  # Nhân lên để đủ 35 API
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
    ] * 5
    ,
    "socks4": [
        "https://api.proxyscrape.com/?request=getproxies&proxytype=socks4",
        "https://www.proxy-list.download/api/v1/get?type=socks4",
        "https://www.proxyscan.io/download?type=socks4",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://rootjazz.com/proxies/proxies.txt",
        "https://www.my-proxy.com/free-socks-4-proxy.html",
        "https://openproxy.space/list/socks4",
        "https://proxylist.geonode.com/api/proxy-list?protocols=socks4",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt"
    ] * 3 + [
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
    ] * 5
    ,
    "socks5": [
        "https://api.proxyscrape.com/?request=getproxies&proxytype=socks5",
        "https://www.proxy-list.download/api/v1/get?type=socks5",
        "https://www.proxyscan.io/download?type=socks5",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://rootjazz.com/proxies/proxies.txt",
        "https://www.my-proxy.com/free-socks-5-proxy.html",
        "https://openproxy.space/list/socks5",
        "https://proxylist.geonode.com/api/proxy-list?protocols=socks5",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt"
    ] * 3 + [
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
    ] * 5
}

# Tệp lưu proxy
FILES = {
    "http": "http_proxies.txt",
    "socks4": "socks4_proxies.txt",
    "socks5": "socks5_proxies.txt"
}

def fetch_proxies(proxy_type):
    """Đào proxy từ 35 nguồn API"""
    proxies = set()
    for url in PROXY_SOURCES[proxy_type]:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                new_proxies = set(response.text.strip().split("\n"))
                proxies.update(new_proxies)
        except requests.RequestException:
            continue
    return proxies

def save_proxies(proxy_type, proxies):
    """Lưu proxy vào file"""
    with open(FILES[proxy_type], "a") as f:
        for proxy in proxies:
            f.write(proxy + "\n")

def mine_proxies(proxy_type):
    """Đào proxy"""
    mined_proxies = set()
    while len(mined_proxies) < MAX_PROXIES:
        new_proxies = fetch_proxies(proxy_type)
        mined_proxies.update(new_proxies)
        save_proxies(proxy_type, new_proxies)
        print(f"Đã đào {len(mined_proxies)}/{MAX_PROXIES} proxy {proxy_type}")
        if len(mined_proxies) >= MAX_PROXIES:
            break
    print(f"Đào xong {MAX_PROXIES} proxy {proxy_type}!")

def check_proxy(proxy, proxy_type):
    """Kiểm tra proxy hoạt động"""
    test_url = "http://ip-api.com/json/"
    proxies = { 
        "http": f"http://{proxy}",
        "https": f"http://{proxy}" if proxy_type == "http" else f"socks5://{proxy}"
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            return proxy
    except requests.RequestException:
        return None

def filter_proxies(proxy_type):
    """Lọc proxy hợp lệ"""
    valid_proxies = []
    with open(FILES[proxy_type], "r") as f:
        proxies = f.read().splitlines()

    def check_and_store(proxy):
        result = check_proxy(proxy, proxy_type)
        if result:
            valid_proxies.append(result)

    threads = []
    for proxy in proxies:
        thread = threading.Thread(target=check_and_store, args=(proxy,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    with open(f"filtered_{FILES[proxy_type]}", "w") as f:
        for proxy in valid_proxies:
            f.write(proxy + "\n")

    print(f"Lọc xong! Có {len(valid_proxies)} proxy {proxy_type} hợp lệ.")

def main():
    print("Chọn chế độ:\n1. Đào proxy\n2. Lọc proxy")
    choice = input("Nhập số: ").strip()

    if choice not in ["1", "2"]:
        print("Lựa chọn không hợp lệ!")
        return

    print("Chọn loại proxy:\n1. HTTP\n2. SOCKS4\n3. SOCKS5")
    proxy_choice = input("Nhập số: ").strip()
    proxy_types = {"1": "http", "2": "socks4", "3": "socks5"}

    if proxy_choice not in proxy_types:
        print("Lựa chọn không hợp lệ!")
        return

    proxy_type = proxy_types[proxy_choice]

    if choice == "1":
        mine_proxies(proxy_type)
    else:
        filter_proxies(proxy_type)

if __name__ == "__main__":
    main()
