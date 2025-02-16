import asyncio
import typer

from rag_foodstuff import (
    fetch_list_products, 
    data_preprocessing, 
    ScrapingProductsPages,
    data_from_raw_pages,
    query_rag
)

app = typer.Typer()

@app.command()
def fetch_products():
    """Собирает список товаров"""
    fetch_list_products('data/products_raw.csv')

@app.command()
def preprocess():
    """Обрабатывает данные товаров, удаляя похожие товары"""
    data_preprocessing('data/products_raw.csv', 'data/products_process.csv')

@app.command()
def scrape_pages():
    """Скачивает страницы товаров"""
    scraper = ScrapingProductsPages('data/products_process.csv', 'data/raw_pages/')
    asyncio.run(scraper.scraping())

@app.command()
def clear_data():
    """Собирает необходимые данные из сырых загруженных страниц"""
    data_from_raw_pages('data/raw_pages', 'data/data_clear_r.csv')

@app.command()
def query(text: str):
    """Текстовый запрос в RAG"""
    query_rag(text)

if __name__ == "__main__":
    app()