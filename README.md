```
rag_foodstuff
├── data
│   ├── data_clear.csv
│   ├── faiss_products_db
│   │   ├── index.faiss
│   │   └── index.pkl
│   ├── products_process.csv
│   ├── products_raw.csv
├── main.py                           # Основная точка входа (CLI)
├── notebook.ipynb                    # Ноутбук с RAG
├── rag_foodstuff                     # Основной пакет проекта (код)
│   ├── __init__.py
│   ├── data_from_pages.py            # 4. Сбор информации о товарах со страниц
│   ├── data_preprocessing.py         # 2. Предобработка ссылок
│   ├── fetch_list_products.py        # 1. Сбор ссылок на товары
│   ├── free_proxy.py                 # Работа с прокси
│   ├── scraping_products_pages.py    # 3. Загрузка сырых страниц
├── README.md
└── requirements.txt
```
