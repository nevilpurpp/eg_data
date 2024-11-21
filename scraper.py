import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import datetime
import csv

# Database connection
def db_connection():
    try:
        conn = sqlite3.connect('egerton_db.db')
        return conn
    except sqlite3.Error as e:
        print("Error while connecting to SQLite database:", e)
        return None

# Write to CSV
def write_to_csv(filename, data, headers):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:  # Write header only for new files
            writer.writerow(headers)
        writer.writerows(data)

# Scraper function
def scraper():
    conn = db_connection()
    if conn is None:
        print("Failed to create database connection.")
        return

    with conn:
        cur = conn.cursor()

        # Scrape recent news
        def recent_news():
            try:
                url = "https://www.egerton.ac.ke/"
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                news_highlights = soup.find_all('div', class_='latest-articles')
                news_data = []

                for highlight in news_highlights:
                    articles = highlight.find_all('div', itemscope=True, itemtype="http://schema.org/Article")
                    for article in articles:
                        title = article.find('span', class_='latest-articles-title').text.strip()
                        link = article.find('a', class_='latest-news-title')['href'].strip()
                        image = article.find('img', class_='lazyload')['data-src'].strip()
                        date = article.find('span', class_='sppb-articles-carousel-meta-date').text.strip() if article.find('span', class_='sppb-articles-carousel-meta-date') else None

                        news_data.append((title, link, image, date))

                cur.execute('''CREATE TABLE IF NOT EXISTS recent_egerton_news (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                Title TEXT,
                                Link TEXT,
                                Image_url TEXT,
                                Date TEXT,
                                UNIQUE (Title, Link, Image_url, Date) ON CONFLICT IGNORE
                               )''')

                write_to_csv('recent_egerton_news.csv', news_data, ['Title', 'Link', 'Image_url', 'Date'])
                cur.executemany('''INSERT OR IGNORE INTO recent_egerton_news (Title, Link, Image_url, Date)
                                    VALUES (?, ?, ?, ?)''', news_data)
            except requests.RequestException as e:
                print("Error fetching recent news:", e)

        # Scrape main news
        def news(url):
            current_page = 1
            all_news_data = []

            while True:
                try:
                    page_url = f"{url}?start={25 * (current_page - 1)}"
                    response = requests.get(page_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')

                    news_articles = soup.find_all('div', class_='w357ui-grid-small ma-article')
                    if not news_articles:
                        break

                    for article in news_articles:
                        title = article.find('h3', class_='w357ui-margin-small-bottom ma-title').find('a').text.strip()
                        link = "https://www.egerton.ac.ke" + article.find('h3', class_='w357ui-margin-small-bottom ma-title').find('a')['href'].strip()
                        image = None
                        image_tag = article.find('div', class_='ma-image').find('img')
                        if image_tag and 'src' in image_tag.attrs:
                            image = "https://www.egerton.ac.ke" + image_tag['src'].strip()

                        date = article.find('div', class_='ma-date').find('time').text.strip()
                        intro = article.find('div', class_='ma-introtext').text.strip()
                        updated_date = datetime.datetime.now()

                        all_news_data.append((title, intro, image, link, date, updated_date))

                    current_page += 1
                except requests.RequestException as e:
                    print("Error fetching news:", e)
                    break

            cur.execute('''CREATE TABLE IF NOT EXISTS egerton_news (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            Title TEXT,
                            Intro TEXT,
                            Image_url TEXT,
                            Link TEXT,
                            Date TEXT,
                            UpdatedDate TIMESTAMP,
                            UNIQUE (Title, Intro, Image_url, Link, Date) ON CONFLICT IGNORE
                           )''')

            write_to_csv('egerton_news.csv', all_news_data, ['Title', 'Intro', 'Image_url', 'Link', 'Date', 'UpdatedDate'])
            cur.executemany('''INSERT OR IGNORE INTO egerton_news (Title, Intro, Image_url, Link, Date, UpdatedDate)
                                VALUES (?, ?, ?, ?, ?, ?)''', all_news_data)

        # Scrape downloads
        def downloads():
            try:
                url = "https://www.egerton.ac.ke/studentdownloads"
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                download_items = soup.find_all('ul', class_='nav menu egerton-padding mod-list')
                downloads_data = []

                for items in download_items:
                    for link in items.find_all('a'):
                        title = link.text.strip()
                        href = link.get('href').strip()
                        full_link = "https://www.egerton.ac.ke" + href
                        file_format = os.path.splitext(href)[1]
                        downloads_data.append((title, full_link, file_format))

                cur.execute('''CREATE TABLE IF NOT EXISTS downloads (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                Title TEXT,
                                Link TEXT,
                                Format TEXT,
                                UNIQUE (Title, Link) ON CONFLICT IGNORE
                               )''')

                write_to_csv('downloads.csv', downloads_data, ['Title', 'Link', 'Format'])
                cur.executemany('''INSERT OR IGNORE INTO downloads (Title, Link, Format)
                                    VALUES (?, ?, ?)''', downloads_data)
            except requests.RequestException as e:
                print("Error fetching downloads:", e)

        # Scrape noticeboard
        def notice_board():
            try:
                url = "https://www.egerton.ac.ke/"
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                quick_links = soup.find_all('ul', class_='nav menu mod-list')
                noticeboard_link = None
                for links in quick_links:
                    for link in links.find_all('a'):
                        if link.text.strip() == 'Notice Board':
                            noticeboard_link = "https://www.egerton.ac.ke" + link.get('href').strip()
                            break

                if noticeboard_link:
                    noticeboard_response = requests.get(noticeboard_link)
                    noticeboard_response.raise_for_status()
                    noticeboard_soup = BeautifulSoup(noticeboard_response.content, 'html.parser')

                    notice_items = noticeboard_soup.find_all('li', class_='allmode-item')
                    notice_data = []
                    for item in notice_items:
                        title = item.find('h4', class_='allmode-title').text.strip()
                        date = item.find('div', class_='allmode-date').text.strip()
                        text = item.find('div', class_='allmode-text').text.strip()
                        notice_data.append((title, date, text))

                    cur.execute('''CREATE TABLE IF NOT EXISTS notice_board_news (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Title TEXT,
                                    Date TEXT,
                                    Article TEXT,
                                    UNIQUE (Title, Date, Article) ON CONFLICT IGNORE
                                   )''')

                    write_to_csv('notice_board_news.csv', notice_data, ['Title', 'Date', 'Article'])
                    cur.executemany('''INSERT OR IGNORE INTO notice_board_news (Title, Date, Article)
                                        VALUES (?, ?, ?)''', notice_data)
            except requests.RequestException as e:
                print("Error fetching notice board:", e)

        # Execute functions
        recent_news()
        news("https://www.egerton.ac.ke/news")
        downloads()
        notice_board()

scraper()
