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