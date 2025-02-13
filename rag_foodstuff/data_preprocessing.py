import re
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN


def data_preprocessing(csv_input: str, csv_output: str) -> None:
    """Функция для удаления похожих товаров по названиям."""

    csv_input = Path(csv_input)
    csv_output = Path(csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)

    def normalize_name(name):
        name = str(name).lower()  # Приводим к нижнему регистру

        units = r'(г|кг|л|шт|упак|см|мг|мл|%|гр|д|×)'
        name = re.sub(rf'[\d]+[.,\d]*\s*{units}|\b{units}\b', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'[^\w\s\-]', '', name)

        return name.strip()

    products = pd.read_csv(csv_input)
    products = products.drop_duplicates(subset='link')

    products['name_norm'] = products['name'].apply(lambda name: normalize_name(name))
    products = products.drop_duplicates(subset='name_norm')

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(products['name_norm'])

    dbscan = DBSCAN(eps=.4, min_samples=1, metric="cosine")
    products.loc[:, 'cluster'] = dbscan.fit_predict(tfidf_matrix)

    cluster_group = products.groupby('cluster')['name_norm'].apply(lambda x: x.str.len().idxmin())
    products = products.loc[cluster_group]

    products = products.drop(['name', 'cluster'], axis=1)
    products = products.rename(columns={'name_norm': 'name'})

    products = products.reset_index(drop=True)
    products.loc[:, 'is_save'] = 0
    products.to_csv(csv_output, index=True)


# def main():
#     data_preprocessing('data/products_raw.csv', 'data/products_process.csv')

# if __name__ == '__main__':
#     main()