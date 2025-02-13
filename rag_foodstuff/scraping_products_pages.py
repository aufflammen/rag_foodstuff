import asyncio
import random
from pathlib import Path
import pandas as pd
from tqdm.asyncio import tqdm

from fake_useragent import UserAgent
import httpx

from .free_proxy import GetFreeProxy


class ScrapingProductsPages:

    def __init__(self, csv_file: str, output_dir: str):
        self.csv_file = csv_file
        self.data = pd.read_csv(csv_file, index_col=0)
        self.data_to_parse = self.data[self.data['is_save'] == 0]

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.proxies = []
        self.useragent = UserAgent(platforms='desktop')


    async def initialize_proxies(self):
        """Получает список рабочих прокси перед запуском парсинга."""
        self.proxies = await GetFreeProxy().get_proxies_list()
        # self.proxies = ['31.204.199.54:81', '128.140.113.110:1080', '59.63.205.36:655', '157.66.122.245:8080', '114.9.26.202:8080', '113.195.172.194:655', '72.10.160.170:9239', '138.59.227.248:999', '218.1.197.91:2324', '72.10.160.90:19003', '223.82.60.230:655', '189.85.82.38:3128', '110.78.85.161:8080', '141.95.1.186:3128', '72.10.160.90:33053', '72.10.160.170:29445', '110.43.221.121:7088', '183.178.50.58:8080', '103.41.88.6:83', '103.164.223.51:8080', '190.60.41.26:999', '157.131.18.67:3128', '177.137.224.22:8081', '182.105.82.38:655', '38.183.146.157:8090', '67.43.236.19:27251', '72.10.160.170:12043', '45.186.6.104:3128', '116.106.190.142:8080', '203.74.125.18:8888', '188.125.169.235:8080', '209.14.119.229:999', '103.138.26.101:8080', '103.167.30.238:64999', '72.10.160.170:16911', '103.169.254.45:6080', '38.51.243.137:9991', '72.10.160.90:29037', '123.184.72.182:1181', '49.0.43.238:39930', '187.251.130.156:8080', '103.166.153.192:8080', '201.91.82.155:3128', '45.58.147.28:3128', '185.215.5.60:3130', '103.148.130.6:8080', '67.43.236.18:18125', '196.192.76.185:3128', '67.43.227.230:26795', '58.59.61.200:10991', '116.193.216.131:8080', '65.108.159.129:8080', '45.236.106.86:8080', '78.129.155.75:8080', '195.181.40.29:8080', '116.203.139.209:5153', '65.20.189.104:9090', '45.123.142.77:8181', '106.115.87.35:9100', '185.191.236.162:3128', '123.125.174.5:5906', '116.169.61.56:10990', '113.160.132.195:8080', '175.29.197.2:63312']

        print(f"✅ Найдено рабочих прокси: {len(self.proxies)}")
        print(self.proxies)
        print()


    async def get_page_with_proxy(self, idx, url, semaphore):
        async with semaphore:
            while True:
                proxy = random.choice(self.proxies)
                headers = {
                    'Accept': '*/*',
                    'User-Agent': self.useragent.random
                }
                try:
                    async with httpx.AsyncClient(proxy=f"http://{proxy}", headers=headers, timeout=25) as client:
                        response = await client.get(url=url)

                    if response.status_code == 200:
                        path = self.output_dir / url.split('/')[-1]  # f"{idx}.html" 
                        path.write_text(response.text, encoding='utf-8')

                        self.data.loc[idx, 'is_save'] = 1
                        self.data.to_csv(self.csv_file, index=True)

                        print(f"✅ Успех! Использован прокси: {proxy}")
                        return
                    else:
                        print(f"❌ Ошибка ({proxy}): {response.status_code}")

                # except Exception:
                #     pass

                except httpx.ConnectTimeout:
                    print(f"⏳ Таймаут подключения ({proxy})")
                except httpx.ProxyError:
                    print(f"🚫 Ошибка прокси: ({proxy})")
                except httpx.RequestError as e:
                    print(f"❌ Ошибка сети ({proxy}): {e}")

    
    async def scraping(self, max_concurrent=60):
        """Основная асинхронная функция парсинга."""
        await self.initialize_proxies()

        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = [
            self.get_page_with_proxy(idx, row['link'], semaphore)
            for idx, row in self.data_to_parse.iterrows()
        ]
        await tqdm.gather(*tasks)



# async def main():
#     scraper = ScrapingProductsPages('data/products_process.csv', 'data/raw_pages/')
#     await scraper.scraping()

# if __name__ == '__main__':
#     asyncio.run(main())
