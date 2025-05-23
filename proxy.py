import asyncio
import aiohttp
import requests
from urllib.parse import urlparse
import re
import os
from datetime import datetime
import platform

# Danh sách 50 nguồn API proxy
PROXY_APIS = {
    'http': [
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://api.proxyscrape.com/?request=getproxies&proxytype=http&country=all',
        'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt',
        'https://vakhov.github.io/fresh-proxy-list/http.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http

.txt',
        'http://pubproxy.com/api/proxy?limit=20&format=txt&type=http',
        'https://api.getproxylist.com/proxy?protocol[]=http',
        'https://proxyelite.info/free-proxy-list/?type=http',
        'https://www.oxylabs.io/free-proxy-list/http.txt',
        'https://proxy.webshare.io/api/v2/proxy/list/?page=1&page_size=10',
        'https://www.advanced.name/freeproxy?type=http',
        'https://gimmeproxy.com/api/getProxy?protocol=http',
        'https://www.proxyscan.io/api/proxy?type=http&limit=10',
        'https://www.scrapingbee.com/freeproxies/http.txt',
        'https://free-proxy-list.net/anonymous-proxy.html',
        'https://www.sslproxies.org/',
        'https://www.google-proxy.net/',
        'https://www.us-proxy.org/',
        'https://free-proxy-list.net/uk-proxy.html',
        'http://spys.me/proxy.txt',
        'https://www.proxynova.com/proxy-server-list/?protocol=http',
        'https://www.geonode.com/free-proxy-list/http',
        'https://www.guru99.com/proxy/http.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt',
        'https://www.freeproxycz.com/free-proxy-list/http',
        'https://api.openproxylist.xyz/http.txt',
        'https://www.proxy-list.download/HTTP',
        'https://freeproxyupdate.com/http',
        'https://proxylist.me/api/proxies/http',
        'https://www.freeproxylists.net/http.txt',
        'https://proxy4free.com/api/http',
        'https://openproxy.space/list/http',
        'https://proxy-list.org/api/http',
        'https://www.freeproxylists.com/http.txt',
        'https://proxy-list.space/api/http',
        'https://my-proxy.com/free-proxy-list/http',
        'https://freeproxychecker.com/api/http',
        'https://proxy6.net/free/http.txt',
        'https://freeproxylists.io/api/http',
        'https://proxy-daily.com/free/http.txt',
        'https://free-proxy-list.com/api/http',
        'https://proxy-list.biz/api/http',
        'https://proxy-list.live/api/http',
        'https://freeproxies.org/api/http',
        'https://proxy-list.info/api/http',
        'https://dailyproxies.net/api/http',
        'https://proxy-list.me/api/http',
        'https://freeproxylist.live/api/http',
        'https://proxy-list.online/api/http'
    ],
    'socks4': [
        'https://www.proxy-list.download/api/v1/get?type=socks4',
        'https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&country=all',
        'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt',
        'https://vakhov.github.io/fresh-proxy-list/socks4.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'http://pubproxy.com/api/proxy?limit=20&format=txt&type=socks4',
        'https://api.getproxylist.com/proxy?protocol[]=socks4',
        'https://proxyelite.info/free-proxy-list/?type=socks4',
        'https://www.oxylabs.io/free-proxy-list/socks4.txt',
        'https://www.advanced.name/freeproxy?type=socks4',
        'https://gimmeproxy.com/api/getProxy?protocol=socks4',
        'https://www.proxyscan.io/api/proxy?type=socks4&limit=10',
        'https://www.scrapingbee.com/freeproxies/socks4.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
        'https://www.freeproxylists.net/socks4.txt',
        'https://proxy4free.com/api/socks4',
        'https://openproxy.space/list/socks4',
        'https://proxy-list.org/api/socks4',
        'https://www.freeproxylists.com/socks4.txt',
        'https://proxy-list.space/api/socks4',
        'https://my-proxy.com/free-proxy-list/socks4',
        'https://freeproxychecker.com/api/socks4',
        'https://proxy6.net/free/socks4.txt',
        'https://freeproxylists.io/api/socks4',
        'https://proxy-daily.com/free/socks4.txt',
        'https://free-proxy-list.com/api/socks4',
        'https://proxy-list.biz/api/socks4',
        'https://proxy-list.live/api/socks4',
        'https://freeproxies.org/api/socks4',
        'https://proxy-list.info/api/socks4'
    ],
    'socks5': [
        'https://www.proxy-list.download/api/v1/get?type=socks5',
        'https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&country=all',
        'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt',
        'https://vakhov.github.io/fresh-proxy-list/socks5.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'http://pubproxy.com/api/proxy?limit=20&format=txt&type=socks5',
        'https://api.getproxylist.com/proxy?protocol[]=socks5',
        'https://proxyelite.info/free-proxy-list/?type=socks5',
        'https://www.oxylabs.io/free-proxy-list/socks5.txt',
        'https://www.advanced.name/freeproxy?type=socks5',
        'https://gimmeproxy.com/api/getProxy?protocol=socks5',
        'https://www.proxyscan.io/api/proxy?type=socks5&limit=10',
        'https://www.scrapingbee.com/freeproxies/socks5.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
        'https://api.openproxylist.xyz/socks5.txt',
        'https://www.freeproxycz.com/free-proxy-list/socks5',
        'https://www.freeproxylists.net/socks5.txt',
        'https://proxy4free.com/api/socks5',
        'https://openproxy.space/list/socks5',
        'https://proxy-list.org/api/socks5',
        'https://www.freeproxylists.com/socks5.txt',
        'https://proxy-list.space/api/socks5',
        'https://my-proxy.com/free-proxy-list/socks5',
        'https://freeproxychecker.com/api/socks5',
        'https://proxy6.net/free/socks5.txt',
        'https://freeproxylists.io/api/socks5',
        'https://proxy-daily.com/free/socks5.txt',
        'https://free-proxy-list.com/api/socks5',
        'https://proxy-list.biz/api/socks5',
        'https://proxy-list.live/api/socks5',
        'https://freeproxies.org/api/socks5',
        'https://proxy-list.info/api/socks5',
        'https://dailyproxies.net/api/socks5',
        'https://proxy-list.me/api/socks5',
        'https://freeproxylist.live/api/socks5',
        'https://proxy-list.online/api/socks5'
    ]
}

# Hàm kiểm tra proxy
async def check_proxy(session, proxy, proxy_type, timeout=5):
    test_urls = {
        'http': 'http://httpbin.org/ip',
        'socks4': 'http://httpbin.org/ip',
        'socks5': 'http://httpbin.org/ip'
    }
    proxies = {
        'http': f'{proxy_type}://{proxy}',
        'https': f'{proxy_type}://{proxy}'
    }
    
    try:
        async with session.get(test_urls[proxy_type], proxies=proxies, timeout=timeout) as response:
            if response.status == 200:
                return True
    except:
        return False
    return False

# Hàm lấy proxy từ nhiều nguồn API
async def fetch_proxies_from_apis(proxy_type):
    proxies = set()
    for api_url in PROXY_APIS[proxy_type]:
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                proxy_list = response.text.splitlines()
                for proxy in proxy_list:
                    proxy = proxy.strip()
                    if proxy and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$', proxy):
                        proxies.add(proxy)
                print(f"Đã lấy {len(proxy_list)} proxy từ {api_url}")
            else:
                print(f"Lỗi khi lấy proxy từ {api_url}: {response.status_code}")
        except Exception as e:
            print(f"Lỗi khi lấy proxy từ {api_url}: {e}")
    return list(proxies)

# Hàm scan proxy từ các API
async def scan_proxies(proxy_type, output_file):
    try:
        proxies = await fetch_proxies_from_apis(proxy_type)
        valid_proxies = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for proxy in proxies:
                tasks.append(check_proxy(session, proxy, proxy_type))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for proxy, result in zip(proxies, results):
                if result:
                    valid_proxies.append(proxy)
                    print(f"Valid {proxy_type} proxy: {proxy}")
        
        # Lưu kết quả vào file
        with open(output_file, 'w') as f:
            for proxy in valid_proxies:
                f.write(f"{proxy}\n")
        print(f"Đã lưu {len(valid_proxies)} proxy hợp lệ vào {output_file}")
        
    except Exception as e:
        print(f"Lỗi khi scan proxy: {e}")

# Hàm lọc proxy từ file txt
async def filter_proxies(proxy_type, input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            proxies = f.read().splitlines()
        
        valid_proxies = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for proxy in proxies:
                proxy = proxy.strip()
                if proxy:
                    tasks.append(check_proxy(session, proxy, proxy_type))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for proxy, result in zip(proxies, results):
                if result:
                    valid_proxies.append(proxy)
                    print(f"Valid {proxy_type} proxy: {proxy}")
        
        # Lưu kết quả vào file
        with open(output_file, 'w') as f:
            for proxy in valid_proxies:
                f.write(f"{proxy}\n")
        print(f"Đã lưu {len(valid_proxies)} proxy hợp lệ vào {output_file}")
        
    except Exception as e:
        print(f"Lỗi khi lọc proxy: {e}")

# Hàm chính
def main():
    print("=== Proxy Scanner & Filter (Multi-API) ===")
    print("1. Scan proxy từ 50 nguồn API")
    print("2. Lọc proxy từ file")
    mode = input("Chọn chế độ (1 hoặc 2): ")
    
    proxy_types = ['http', 'socks4', 'socks5']
    print("\nChọn loại proxy:")
    for i, p_type in enumerate(proxy_types, 1):
        print(f"{i}. {p_type.upper()}")
    proxy_choice = int(input("Nhập số (1-3): ")) - 1
    proxy_type = proxy_types[proxy_choice]
    
    # Tạo tên file đầu ra
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"valid_{proxy_type}_proxies_{timestamp}.txt"
    
    if mode == '1':
        asyncio.run(scan_proxies(proxy_type, output_file))
    elif mode == '2':
        input_file = input("Nhập đường dẫn file proxy (.txt): ")
        asyncio.run(filter_proxies(proxy_type, input_file, output_file))
    else:
        print("Chế độ không hợp lệ!")

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
