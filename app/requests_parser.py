import requests
from bs4 import BeautifulSoup
import csv
from clickhouse_driver import Client, errors
import re
import logging

clickhouse_client = Client('127.0.0.1', port=9000)

logging.basicConfig(
    filename='db_insert.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

url = 'https://book24.ru/catalog/poeziya-1625/'
pages = 221

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}

with open("Поэзия.csv", mode="w", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter=";", lineterminator="\r")
    file_writer.writerow(["ISBN", "Название книги", "Автор", "Издательство", "Цена", "Рейтинг", "Количество оценок", "Раздел", 
                          "Подраздел", "Возрастное ограничение", "Переплет", "Бумага", "Год издания", "Количество страниц", "Описание"])

    for page in range(1, pages):
        print(f'Страница {page} из {pages}-------------------------------------------------------------------')
        
        if page > 1:
            page_url = f'{url}page-{page}/'
        else:
            page_url = url
        
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all book links on the current page
        book_links = soup.select("div.product-card__content > a")
        
        hrefs = [link['href'] for link in book_links]

        for href in hrefs:
            print(href)
            books_dict = {}
            name = ''
            rating = None
            name_author = ''
            price_old = None
            description = ''
            amount_of_evaluation = None
            chapter = ''
            sub_chapter = ''
            publisher = ''
            age_restriction = ''
            binding = ''
            year = None
            amount_of_pages = None
            paper = ''
            ISBN = ''


            book_response = requests.get(f'https://book24.ru{href}', headers=headers)
            book_soup = BeautifulSoup(book_response.content, 'html.parser')

            try:
                name = book_soup.select_one("h1.product-detail-page__title").get_text(strip=True)
                
                author_info = book_soup.select("dt.product-characteristic__label-holder")
                if author_info and author_info[0].get_text(strip=True) == 'Автор:':
                    author = author_info[0].find_next_sibling("dd").get_text(strip=True)
                    name_author = author

                if not name_author:
                    name_author = 'No author'
            except Exception:
                name = ''

            characteristics = book_soup.select("dl.product-characteristic__list div.product-characteristic__item")

            # Publisher
            try:
                for characteristic in characteristics:
                    if 'Издательство:' in characteristic.get_text():
                        publisher = characteristic.find("dd").get_text(strip=True)
                        break
            except:
                publisher = ''

            # ISBN
            try:
                for characteristic in characteristics:
                    if 'ISBN:' in characteristic.get_text():
                        ISBN = characteristic.find("dd").get_text(strip=True)
                        break
            except:
                ISBN = ''

            # Age
            try:
                for characteristic in characteristics:
                    if 'Возрастное ограничение:' in characteristic.get_text():
                        age_restriction = characteristic.find("dd").get_text(strip=True)
                        break
            except:
                age_restriction = ''

            # Binding
            try:
                for characteristic in characteristics:
                    if 'Переплет:' in characteristic.get_text():
                        binding = characteristic.find("dd").get_text(strip=True)
                        break
            except:
                binding = ''

            # Paper
            try:
                for characteristic in characteristics:
                    if 'Бумага:' in characteristic.get_text():
                        paper = characteristic.find("dd").get_text(strip=True)
                        break
            except:
                paper = ''

            # Amount of pages
            try:
                for characteristic in characteristics:
                    if 'Количество страниц:' in characteristic.get_text():
                        amount_of_pages = int(characteristic.find("dd").get_text(strip=True))
                        break
            except:
                amount_of_pages = None

            # Year
            try:
                for characteristic in characteristics:
                    if 'Год издания:' in characteristic.get_text():
                        year = int(characteristic.find("dd").get_text(strip=True))
                        break
            except:
                year = None

            # Price
            try:
                #price_new = re.sub(r'\s+', '', book_soup.select_one("span.app-price.product-sidebar-price__price").get_text(strip=True)).replace('₽', '').replace(',', '.')
                price_old = float(re.sub(r'\s+', '', book_soup.select_one("span.app-price.product-sidebar-price__price").get_text(strip=True).replace('₽', '')).replace(',', '.'))
            except:
                price_old = None

            # Rating
            try:
                rating = float(book_soup.select_one("span.rating-widget__main-text").get_text(strip=True).replace(',', '.'))
            except:
                rating = None

            # Evaluation count
            try:
                amount_of_evaluation = int(book_soup.select_one("span.rating-widget__other-text").get_text(strip=True).replace('(', '').replace(')', '').replace('K', '000').strip())
            except:
                amount_of_evaluation = None

            # Chapter and Sub-chapter
            try:
                breadcrumbs = book_soup.select("ol.breadcrumbs__list li.breadcrumbs__item")
                chapter = breadcrumbs[-3].get_text(strip=True)
                sub_chapter = breadcrumbs[-2].get_text(strip=True)
            except:
                chapter = ''
                sub_chapter = ''

            # Description
            try:
                description_parts = book_soup.select("div.product-about.product-detail-page__product-about > div.product-about__text > p")
                if len(description_parts) == 1:
                    description = re.sub(r'\s+', ' ', re.sub(r'\n+', ' ', re.sub(r'\s*\.\s*', ' ', description_parts[0].get_text()))).strip()

                else:
                    description = ' '.join(
                        re.sub(r'\n+', ' ', re.sub(r'\. \.', '. ', re.sub(r'… \.', '. ', re.sub(r'\s*(\.\s*){2,}', '', part.get_text())))).strip()
                        for part in description_parts
                    )
            except Exception:
                description = ''

            # Writing to CSV
            file_writer.writerow([ISBN, name, name_author, publisher, price_old, rating, amount_of_evaluation, chapter, sub_chapter, age_restriction, binding, paper, year, amount_of_pages, description])

            print(f'ISBN: {ISBN}')
            print(f'Название: {name}')
            print(f'Автор: {name_author}')
            print(f'Год издания: {year}')
            print(f'Издательства: {publisher}')
            print(f'Цена: {price_old}')
            print(f'Рейтинг: {rating}')
            print(f'Количество оценок: {amount_of_evaluation}')
            print(f'Возрастное ограничение: {age_restriction}')
            print(f'Раздел: {chapter}')
            print(f'Подраздел: {sub_chapter}')
            print(f'Описание: {description[:10]}')
            print(f'Переплет: {binding}')
            print(f'Бумага: {paper}')
            print(f'Количество страниц: {amount_of_pages}')

            print("----------------------------------------------------")

            max_id = clickhouse_client.execute('SELECT max(id) FROM book_recommendation.books')[0][0]

            new_id = (max_id + 1) if max_id is not None else 1

            try:
                clickhouse_client.execute(
                    'INSERT INTO book_recommendation.books (id, ISBN, title, author, year, age, pagesAmount, publisher, price, rating, review_count, section, subsection, paper, binding, description) VALUES', 
                    [(new_id, ISBN, name, name_author, year, age_restriction, amount_of_pages, publisher, price_old, rating, amount_of_evaluation, chapter, sub_chapter, paper, binding, description)]
                )
                logging.info(f"The entry was successfully added with the ID: {new_id}.")
            except errors.ServerException as e:
                error_message = '\n'.join(str(e).splitlines()[0:2]).replace(' Stack trace:', '')
                logging.error(f"Server error: {error_message}")
                
                if "duplicate" in str(e).lower():
                    logging.error("An entry already exists. The entry will not be added.")
                
            except Exception as e:
                logging.error(f"An error occurred while recording: {e}")
                
