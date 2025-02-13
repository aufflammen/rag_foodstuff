import time
import re
import csv
from tqdm.auto import tqdm
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = 'https://vkusvill.ru'
useragent = UserAgent(platforms='desktop')
headers = {
    'Accept': '*/*',
    'User-Agent': useragent.random
}


def get_categories() -> list[list]:
    """Получение ссылок на категории товаров из белого списка."""
    
    val_cat = {
        'Готовая еда',
        'Сладости и десерты',
        'Овощи, фрукты, ягоды, зелень',
        'Хлеб и выпечка',
        'Молочные продукты, яйцо',
        'Мясо, птица',
        'Рыба, икра и морепродукты',
        'Колбаса, сосиски, деликатесы',
        'Замороженные продукты',
        'Сыры',
        'Напитки',
        'Кафе',
        'Орехи, чипсы и снеки',
        'Супермаркет',
        'Особое питание',
        'Вегетарианское и постное',
        'Мороженое',
        'Крупы, макароны, мука',
        'Консервация',
        'Чай и кофе',
        'Масла, соусы, специи, сахар и соль',
}
    src = requests.get(url + '/goods', headers=headers)
    soup = BeautifulSoup(src.text, 'lxml')

    menu = soup.find_all('li', 'VVCatalog2020Menu__Item')
    
    result = []
    for item in menu:
        link = item.find('a', 'VVCatalog2020Menu__Link')['href']
        name = item.find('span', 'VVCatalog2020Menu__LinkCol _text rtext').text.strip()
        name = re.sub(r'\s+', ' ', name)
        if name in val_cat:
            result.append([name, url + link])

    return result



service = Service('/snap/bin/geckodriver')
options = Options()
options.set_preference('general.useragent.override', useragent.random)
options.add_argument("--headless")


def get_list_products_from_page(url: str) -> list[list]:
    """Получение ссылок на все товары со страницы."""
        
    def scroll_down():
        """Прокрутка страницы вниз"""
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)

    driver = webdriver.Firefox(service=service, options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    scroll_down()

    # Закрываем уведомление о куках (если есть)
    try:
        cookie_close = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'Cookie__close')))
        cookie_close.click()
    except:
        pass

    # Кликаем на "Показать еще" (если есть кнопка)
    try:
        time.sleep(1)
        load_more_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "js-catalog-load-more")))
        load_more_button.click()
    except:
        pass

    # Прокручиваем страницу до тех пор, пока загружаются новые товары
    cnt = 0
    while True:
        items_before = len(driver.find_elements(By.CLASS_NAME, 'ProductCards__item'))
        scroll_down()
        time.sleep(.5)
        items_after = len(driver.find_elements(By.CLASS_NAME, 'ProductCards__item'))

        if items_after == items_before:
            cnt += 1
            if cnt > 5:
                break
        else:
            cnt = 0

    products = driver.find_elements(By.CSS_SELECTOR, 'a.ProductCard__link')

    data = []
    for prod in products:
        title = prod.get_attribute('title').strip()
        link = prod.get_attribute('href').strip()
        data.append([title, link])

    # Close driver
    driver.close()
    driver.quit()

    return data


def fetch_list_products(csv_output: str) -> None:
    """Функция для каждой категории собирает список ссылок для всех товаров и записывает в csv файл."""

    csv_output = Path(csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)

    categories = get_categories()

    with open(csv_output, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'link', 'category'])

        for cat_name, cat_link in tqdm(categories):
            products = get_list_products_from_page(cat_link)
            writer.writerows([prod + [cat_name] for prod in products])
            time.sleep(10)

# def main():
#     fetch_list_products('data/products_raw.csv')

# if __name__ == '__main__':
#     main()
