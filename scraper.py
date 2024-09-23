import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('egerton_db.db')
        return conn
    except sqlite3.Error as e:
        print("Error while connecting to SQLite database:", e)
        return conn


def scraper():
    conn = db_connection()
    if conn is None:
        print("Failed to create database connection.")
        return

    cur = conn.cursor()

    url = "https://www.egerton.ac.ke/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # University news
    news_highlights = soup.find_all('div', class_='latest-articles')
    news_titles = []
    news_links = []
    news_images = []
    news_dates = []

    for highlight in news_highlights:
        articles = highlight.find_all('div', itemscope=True, itemtype="http://schema.org/Article")
        for article in articles:
            title = article.find('span', class_='latest-articles-title').text.strip()
            link = article.find('a', class_='latest-news-title')['href'].strip()
            image = article.find('img', class_='lazyload')['data-src'].strip()
            date = article.find('span', class_='sppb-articles-carousel-meta-date').text.strip() if article.find('span',
                                                                                                                class_='sppb-articles-carousel-meta-date') else None
            # print(title)
            # print(link)
            # print(image)
            # print(date)

            news_titles.append(title)
            news_links.append(link)
            news_images.append(image)
            news_dates.append(date)

    # Quick links
    quick_links = soup.find_all('ul', class_='nav menu mod-list')
    quick_link_titles = []
    quick_link_links = []

    for links in quick_links:
        for link in links.find_all('a'):
            title = link.text.strip()
            href = link.get('href').strip()

            quick_link_titles.append(title)
            quick_link_links.append(href)

    # Noticeboard news
    noticeboard_link = None
    for i, title in enumerate(quick_link_titles):
        if title == 'Notice Board':
            noticeboard_link = quick_link_links[i]
            break

    if noticeboard_link:
        noticeboard_link = "https://www.egerton.ac.ke" + noticeboard_link
        noticeboard_response = requests.get(noticeboard_link)
        noticeboard_soup = BeautifulSoup(noticeboard_response.content, 'html.parser')

        notice_items = noticeboard_soup.find_all('li', class_='allmode-item')
        notice_titles = []
        notice_dates = []
        notice_texts = []

        for item in notice_items:
            title = item.find('h4', class_='allmode-title').text.strip()
            date = item.find('div', class_='allmode-date').text.strip()
            text = item.find('div', class_='allmode-text').text.strip()
            # print(title, date, text)

            notice_titles.append(title)
            notice_dates.append(date)
            notice_texts.append(text)

        noticeboard_df = pd.DataFrame({
            'Title': notice_titles,
            'Date': notice_dates,
            'Article': notice_texts
        })
        cur.execute('''
          CREATE TABLE IF NOT EXISTS notice_board_news (
              id INTEGER PRIMARY KEY,
              Title TEXT,
              Date CHAR(50),
              Article TEXT
          )
        ''')

        # Saving noticeboard data to the database
        noticeboard_df.to_sql('notice_board_news', conn, if_exists='append', index=False)

    # News DataFrame
    news_df = pd.DataFrame({
        'Title': news_titles,
        'Link': news_links,
        'Image_url': news_images,
        'Date': news_dates
    })

    # Quick Links DataFrame
    quick_links_df = pd.DataFrame({
        'Title': quick_link_titles,
        'Link': quick_link_links
    })

    # Creating and saving news and quick links tables in the database
    cur.execute('''CREATE TABLE IF NOT EXISTS egerton_news (
                   id INTEGER PRIMARY KEY, 
                   Title TEXT,
                   Image_url STRING,
                   Link STRING,
                   Date CHAR(50)
                   )''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS quick_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Link TEXT
        )
    ''')

    # Saving data to database
    news_df.to_sql('egerton_news', conn, if_exists='append', index=False)
    quick_links_df.to_sql('egerton_quick_links', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()


# Running the scraper function
scraper()
