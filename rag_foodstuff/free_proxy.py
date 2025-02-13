import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm.asyncio import tqdm
from pathlib import Path


class GetFreeProxy:
    def __init__(self):
        self.proxy_sources = [
            "https://www.sslproxies.org/",
            # "https://free-proxy-list.net/",
            # "https://api.proxyscrape.com/v2/?request=getproxies&timeout=5000&country=all",
        ]
        self.proxy_file = set(Path('data/proxyscrape.txt').read_text(encoding='utf-8').strip().split('\n'))

        self.useragent = UserAgent(platforms='desktop')
        self.test_url = 'https://vkusvill.ru'


    async def get_proxies_list(self):
        """Получает список бесплатных прокси и проверяет их перед добавлением."""
        tasks = [self.fetch_proxies(url) for url in self.proxy_sources]
        all_proxies = await asyncio.gather(*tasks)
        unique_proxies = {proxy for proxies in all_proxies for proxy in proxies}

        if self.proxy_file is not None:
            unique_proxies.update(self.proxy_file)

        print(f"🟡 Количество proxy для проверки: {len(unique_proxies)}")
        valid_proxies_list =  await self.validate_proxies(list(unique_proxies))
        print(f"✅ Найдено рабочих прокси: {len(valid_proxies_list)}")
        print(valid_proxies_list)

        return valid_proxies_list


    async def fetch_proxies(self, url):
        """Парсит прокси с указанного URL."""
        try:
            headers = {
                'Accept': '*/*',
                'User-Agent': self.useragent.random
            }

            async with httpx.AsyncClient(headers=headers, timeout=10) as client:
                response = await client.get(url)

            soup = BeautifulSoup(response.text, "lxml")
            proxies = soup.find("textarea", "form-control").text.split("\n")[3:-1]

            return [proxy.strip() for proxy in proxies if proxy.strip()]
        except Exception:
            return []


    async def validate_proxies(self, proxies, max_concurrent=20): 
        """Асинхронно проверяет работоспособность прокси."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def check(proxy):
            async with semaphore:
                if await self.check_proxy(proxy):
                    return proxy

        tasks = [check(proxy) for proxy in proxies]
        valid_proxies = await tqdm.gather(*tasks)
        return [x for x in valid_proxies if x is not None]
    

    async def check_proxy(self, proxy):
        """Проверяет один прокси."""
        headers = {
            'Accept': '*/*',
            'User-Agent': self.useragent.random
        }
        
        try:
            async with httpx.AsyncClient(headers=headers, proxy=f"http://{proxy}", timeout=20) as client:
                response = await client.get(self.test_url)
                return response.status_code == 200
        except Exception:
            return False
        

# async def main():
#     await GetFreeProxy().get_proxies_list()

# if __name__ == '__main__':
#     asyncio.run(main())