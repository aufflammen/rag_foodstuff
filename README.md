# RAG Foodstuff

Проект **RAG Foodstuff** представляет собой систему для работы с данными о продуктах питания, их обработки и генерации персонализированных планов питания с использованием технологии **Retrieval-Augmented Generation (RAG)**. В основе системы лежит **LLM (Ollama/GigaChat)**, которая использует векторную базу данных **FAISS** для поиска релевантных продуктов и формирования ответов на запросы пользователя.

## Структура проекта

```
rag_foodstuff
├── data
│   ├── data_clear.csv               # Готовые данные, полученные со страниц товаров
│   ├── faiss_products_db            # Векторная база данных FAISS
│   │   ├── index.faiss
│   │   └── index.pkl
│   ├── products_process.csv         # Промежуточные данные о продуктах с удаленными дубликатами
│   ├── products_raw.csv             # Сырые данные о продуктах (название, категория, ссылка)
├── main.py                          # Основная точка входа (CLI)
├── notebook.ipynb                   # Ноутбук с демонстрацией RAG
├── rag_foodstuff                    # Основной код проекта
│   ├── __init__.py
│   ├── fetch_list_products.py       # Сбор ссылок на товары
│   ├── data_preprocessing.py        # Предобработка ссылок, удаление дублей
│   ├── free_proxy.py                # Выбор рабочих прокси из публичных источников
│   ├── scraping_products_pages.py   # Загрузка сырых страниц
│   ├── data_from_pages.py           # Сбор информации о товарах со страниц
│   ├── rag_pipeline.py              # RAG pipline для генерации ответов
├── README.md                        # Документация
└── requirements.txt                 # Зависимости
```

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/aufflammen/rag_foodstuff.git
cd rag_foodstuff 
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

Проект предоставляет CLI-интерфейс для выполнения различных задач. Для запуска используйте команду:

```bash
python -m main {COMMAND}
```

```
╭─ Доступные команды ───────────────────────────────────────────────────────────╮
│ fetch-products   Собирает список товаров                                      │
│ preprocess       Обрабатывает данные товаров, удаляя похожие товары           │
│ scrape-pages     Скачивает страницы товаров                                   │
│ clear-data       Собирает необходимые данные из сырых загруженных страниц     │
│ query {TEXT}     Текстовый запрос в RAG                                       │
╰───────────────────────────────────────────────────────────────────────────────╯
```

## Ноутбук `notebook.ipynb`

Ноутбук содержит демонстрацию работы RAG-пайплайна, включая загрузку данных, создание векторной базы и генерацию ответов.