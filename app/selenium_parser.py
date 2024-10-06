from pprint import pprint
# from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import csv
from clickhouse_driver import Client

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)

hrefs = []
books_dict = {}
books_list = []

clickhouse_client = Client('127.0.0.1', port=9000)

url = 'https://book24.ru/catalog/fiction-1592/'

driver.get(url)
time.sleep(1)
html = driver.page_source

amount_of_pages = driver.find_element(By.XPATH, "//li[@class='pagination__button-item'][last()]/a").text #получаем кол-во страниц

with open("books.csv", mode="w", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter=";", lineterminator="\r")
    file_writer.writerow(["Название книги", "Автор", "Издательство", "Цена без скидки", "Цена со скидкой", "Рейтинг", "Количество оценок", "Раздел", "Подраздел", "Описание"])

    for page in range(164, int(amount_of_pages)):
        print(f'Страница {page} из {amount_of_pages}-------------------------------------------------------------------')
        hrefs = []

        if page > 1:
            url = 'https://book24.ru/catalog/fiction-1592/' + f'page-{page}/'
            driver.get(url)
        else:
            url = 'https://book24.ru/catalog/fiction-1592/'
            driver.get(url)
        time.sleep(1)
        new_content = driver.find_elements(By.XPATH, "//div[@class='product-card__content']/a")  # получаем книги с 1 страницы

        for book in new_content:
            hrefs.append(
                book.get_attribute("href"))  # ссылки на книги каждой страницы

        for href in hrefs:
            print(href)
            books_dict = {}
            name = ''
            rating = 0.0
            name_author = ''
            price_new = 0.0
            price_old = 0.0
            description = ''
            amount_of_evaluation = 0
            chapter = ''
            sub_chapter = ''
            publisher = ''

            driver.get(href)
            time.sleep(1)
            try:
                name = driver.find_element(By.CSS_SELECTOR, "h1[class='product-detail-page__title']")
                name = name.get_attribute(
                        "innerHTML")
                name = name.strip()

                if name.find(':') != -1: #если в названии уже есть автор, возьмем его
                    index = name.find(':')
                    name_author = name[:index]

                    name = name[index + 2:]
                    name = name.strip()

                else: #если нет, то получим из характеристик
                    characteristics = driver.find_elements(By.CSS_SELECTOR,
                                                    "dt[class='product-characteristic__label-holder']")
                    characts = characteristics[0].find_element(By.CSS_SELECTOR,
                                                        "span").get_attribute(
                        "innerHTML")

                    if characts == ' Автор: ':
                        author = driver.find_element(By.XPATH,
                                                    "//dt[@class ='product-characteristic__label-holder']/following-sibling::dd")

                        try:
                            name_author = author.find_element(By.CSS_SELECTOR,
                                                            "a[class='product-characteristic-link smartLink']").get_attribute(
                                "title")

                        except:
                            name_author = author.get_attribute("innerHTML")
                            name_author = name_author.strip()

                    if name_author == '':
                        name_author = 'No author'

            except Exception as ex:
                name = 'No name'

            # -----------------------------------Издательство-----------------------------------------------
            try:
                company_list = []
                characteristic_blocks = driver.find_elements(By.XPATH, "//dl[@class='product-characteristic__list']")[0]
                characteristics = characteristic_blocks.find_elements(By.CSS_SELECTOR, "div[class='product-characteristic__item']")
                for i in range(len(characteristics)):
                    if characteristics[i].find_element(By.CSS_SELECTOR, "dt[class='product-characteristic__label-holder']").find_element(By.CSS_SELECTOR, "span").get_attribute("innerHTML") == ' Издательство: ':
                        print(f'1: {characteristics[i]}')
                        companies = characteristics[i].find_element(By.CSS_SELECTOR, "dd[class ='product-characteristic__value']").find_elements(By.CSS_SELECTOR, "a")
                        for company in companies:
                            # Получаем заголовок, убираем пробелы и добавляем в список
                            title = company.get_attribute("title").strip()
                            company_list.append(title)

                        # Объединяем элементы списка в строку, разделяя их запятой
                        publisher = ', '.join(company_list)
            except:
                publisher = 'No publisher'
            # -----------------------------------ЦЕНА---------------------------

            try:
                symbols = '&nbsp;'
                price_new = driver.find_element(By.CSS_SELECTOR,
                                                "span[class='app-price product-sidebar-price__price']").get_attribute(
                    "innerHTML")
                price_new = price_new[:price_new.find('₽')]
                price_new = price_new.replace(symbols, '').replace(',', '.').strip()

                try:
                    price_old = driver.find_element(By.CSS_SELECTOR,
                                                    "span[class='app-price product-sidebar-price__price-old']").get_attribute(
                        "innerHTML")
                    price_old = price_old[:price_old.find('₽')]
                    price_old = price_old.replace('&nbsp;', '').replace(',', '.').strip()
                except Exception as ex:
                    price_old = price_new

            except:
                price_old = 0.0
                price_new = 0.0


            # -------------------------------------рейтинг--------------------------------
            try:
                rating = driver.find_element(By.CSS_SELECTOR, "span[class='rating-widget__main-text']").text
                rating = rating.replace(',', '.').strip()

            except:
                rating = 0.0

            try:
                amount_of_evaluation = (driver.find_element(By.CSS_SELECTOR,
                                                            "span[class='rating-widget__other-text']").text).replace('(', '').replace(')', '')
                if 'K' in amount_of_evaluation:
                    amount_of_evaluation = amount_of_evaluation.replace('K', '000').strip()

            except:
                amount_of_evaluation = 0

            #---------------------------------------раздел----------------------------------
            try:

                type = driver.find_element(By.CSS_SELECTOR, "ol[class='breadcrumbs__list']").find_elements(By.CSS_SELECTOR, "li[class='breadcrumbs__item']")
                sub_chapter = type[-1].find_element(By.CSS_SELECTOR, "a").find_element(By.CSS_SELECTOR, "span").text
                chapter = type[-2].find_element(By.CSS_SELECTOR, "a").find_element(By.CSS_SELECTOR, "span").text

                sub_chapter = sub_chapter.strip()
                chapter = chapter.strip()

            except:
                sub_chapter = 'No subchapter'
                chapter = 'No chapter'


            #------------------------------------------ОПИСАНИЕ-----------------------------------------------------

            try:
                description_parts = driver.find_elements(By.XPATH,
                                                "//div[@class='product-about product-detail-page__product-about']/div[@class='product-about__text']/p")
                for part in description_parts:
                    description += part.text
                    description += ' '
                    description = description.strip()

            except Exception as ex:
                description = 'No description'

            books_dict['name'] = name
            books_dict['name_author'] = name_author
            books_dict['price_old'] = float(price_old)
            books_dict['price_new'] = float(price_new)
            books_dict['rating'] = float(rating)
            books_dict['amount_of_evaluation'] = int(amount_of_evaluation)
            books_dict['chapter'] = chapter
            books_dict['sub_chapter'] = sub_chapter
            books_dict['description'] = description
            books_dict['publisher'] = publisher

            file_writer.writerow([name, name_author, publisher, price_old, price_new, rating, amount_of_evaluation, chapter, sub_chapter, description])

            print(f'Название: {name}')
            print(f'Автор: {name_author}')
            print(f'Издательства: {publisher}')
            print(f'Цена без скидки: {price_old}')
            print(f'Цена со скидкой: {price_new}')
            print(f'Рейтинг: {rating}')
            print(f'Количество оценок: {amount_of_evaluation}')
            print(f'Раздел: {chapter}')
            print(f'Подраздел: {sub_chapter}')
            print(f'Описание: {description[:10]}')
            print("----------------------------------------------------")

            # Получение максимального значения id
            max_id = clickhouse_client.execute('SELECT max(id) FROM book_recommendation.books')[0][0]

            # Если таблица пуста, max_id будет None, поэтому мы присваиваем 0
            new_id = (max_id + 1) if max_id is not None else 1

            clickhouse_client.execute('INSERT INTO book_recommendation.books (id, title, author, publisher, price_without_discount, price_with_discount, rating, review_count, section, subsection, description) VALUES', 
                                      [(new_id, name, name_author, publisher, float(price_old), float(price_new), float(rating), int(amount_of_evaluation), chapter, sub_chapter, description)])
