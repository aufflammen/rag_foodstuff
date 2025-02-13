from bs4 import BeautifulSoup
import pandas as pd
import re
from pathlib import Path
from tqdm.auto import tqdm


def clear_text(text):
    return re.sub(r'\s+', ' ', text).lower().strip()

def clear_title(text):
    units = r'(г|кг|л|шт|упак|см|мг|мл|%|гр|д|×)'
    text = re.sub(rf'[\d]+[.,\d]*\s*{units}|\b{units}\b', '', text)
    return text

def replace_keys(data):
    # Проверяет наличие ключей в словаре и заменяет их
    if 'энергетическая ценность' in data:
        data['energy_value'] = data.pop('энергетическая ценность')
    if 'ккал' in data:
        data['energy_value'] = data.pop('ккал')
    if 'белки' in data:
        data['proteins'] = data.pop('белки')
    if 'жиры' in data:
        data['fats'] = data.pop('жиры')
    if 'углеводы' in data:
        data['carbs'] = data.pop('углеводы')
    return data


def data_from_raw_pages(pages_dir: str, csv_output: str):
    result = []

    raw_pages = list(Path(pages_dir).glob('*.html'))
    for path_page in tqdm(raw_pages):
        page = path_page.read_text()
        soup = BeautifulSoup(page, 'lxml')

        data = {}

        data['title'] = clear_title(clear_text(soup.find('h1', 'Product__title').text))
        data['price'] = clear_text(soup.find('span', 'Price').text)
        try:
            data['category'] = clear_text(soup.find_all('span', itemprop='name')[3].text)
            data['subcategory'] = clear_text(soup.find_all('span', itemprop='name')[2].text)
        except:
            pass

        try:
            data['weight'] = clear_text(soup.find('div', 'ProductCard__weight').text)
        except:
            pass

        nutritional_names = [x.text.strip().split(',')[0].lower() for x in soup.find_all('div', 'VV23_DetailProdPageAccordion__EnergyDesc')]
        nutritional_values = [float(x.text.strip()) for x in soup.find_all('div', 'VV23_DetailProdPageAccordion__EnergyValue')]
        nutritional = {k: v for k, v in zip(nutritional_names, nutritional_values)}

        if len(nutritional) == 0:
            try:
                nutritional_raw = (
                    soup
                    .find('div', 'VV23_DetailProdPageInfoDescItem__Title', string=re.compile(r'Пищевая\s*и\s*энергетическая\s*ценность'))
                    .find_next('div', 'VV23_DetailProdPageInfoDescItem__Desc')
                ).text
                nutritional_raw = clear_text(nutritional_raw)

                r_num = r'\d+[\.,]?\d*'
                r_kj = r'к[-\s/]?дж'
                r_nutritional = rf'(энергетическая ценность|белки|жиры|углеводы)[^\d]*?({r_num})'

                nutritional_raw = re.sub(rf'(100|{r_num}\s*{r_kj}|{r_kj}\s*{r_num})', '', nutritional_raw)
                nutritional = re.findall(r_nutritional, nutritional_raw)
                nutritional = {k: float(v.replace(',', '.')) for k, v in nutritional}
            except:
                pass

        nutritional = replace_keys(nutritional)
        data.update(nutritional)

        try:
            composition = (
                soup
                .find('div', 'VV23_DetailProdPageInfoDescItem__Title', string=re.compile(r'Состав'))
                .find_next('div', 'VV23_DetailProdPageInfoDescItem__Desc')
            ).text
            data['composition'] = clear_text(composition)
        except:
            pass

        result.append(data)

    result = pd.DataFrame(result)
    result.to_csv(csv_output)