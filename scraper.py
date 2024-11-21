import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import os
import datetime
import schedule
import time

# Database connection
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('egerton_db.db',)
        return conn
    except sqlite3.Error as e:
        print("Error while connecting to SQLite database:", e)
        return conn

# Main scraper function
def scraper():
 
    conn = db_connection()
    if conn is None:
        print("Failed to create database connection.")
        return

    cur = conn.cursor()

    # Scrape recent news
    def recent_news():
        
        url = "https://www.egerton.ac.ke/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

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
                date = article.find('span', class_='sppb-articles-carousel-meta-date').text.strip() if article.find('span', class_='sppb-articles-carousel-meta-date') else None
              
            
                news_titles.append(title)
                news_links.append(link)
                news_images.append(image)
                news_dates.append(date)
               
                

        news_df = pd.DataFrame({
            'Title': news_titles,
            'Link': news_links,
            'Image_url': news_images,
            'Date': news_dates,
           
        })

        cur.execute('''CREATE TABLE IF NOT EXISTS recent_egerton_news (
                        id INTEGER PRIMARY KEY, 
                        Title TEXT,
                        Link STRING,
                        Image_url STRING,
                        Date CHAR(50),
                        UNIQUE ( id, Title, Intro, Image_url, Link, Date) ON CONFLICT IGNORE
                       )''')

        
        news_df.to_sql('recent_egerton_news',  conn,  if_exists='append', index=False)

    
    def news(url):
        current_page = 1
        has_next_page = True
        all_news_data = []
        
        while has_next_page:
            url = f"{url}?start={25 * (current_page - 1)}" 
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            news_articles = soup.find_all('div', class_='w357ui-grid-small ma-article')
            news_data = []

            for article in news_articles:
                title = article.find('h3', class_='w357ui-margin-small-bottom ma-title').find('a').text.strip()
                link = article.find('h3', class_='w357ui-margin-small-bottom ma-title').find('a')['href'].strip()
                full_link = "https://www.egerton.ac.ke" + link

                image_tag = article.find('div', class_='ma-image').find('img')
                image = image_tag['src'].strip() if image_tag and 'src' in image_tag.attrs else None
                if image:
                    full_image_url = "https://www.egerton.ac.ke" + image
                    try:
                        image_response = requests.get(full_image_url, stream=True)
                        image_response.raise_for_status()
                        filename = os.path.join("images", image.split('/')[-1])
                        os.makedirs("images", exist_ok=True)
                        with open(filename, 'wb') as f:
                            for chunk in image_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading image {image}: {e}")
                        image = None  

                date = article.find('div', class_='ma-date').find('time').text.strip()
                intro = article.find('div', class_='ma-introtext').text.strip()
                updated_date = datetime.datetime.now()

                news_data.append({
                    'Title': title,
                    'Link': full_link,
                    'Image_url': image,
                    'Date': date,
                    'Intro': intro,
                    'UpdatedDate': updated_date
                })
            all_news_data.extend(news_data)
            has_next_page = soup.find('a', class_='next') is not None
            current_page += 1

        return all_news_data

    def downloads():
        url = "https://www.egerton.ac.ke/studentdownloads"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        download_items = soup.find_all('ul', class_='nav menu egerton-padding mod-list')
        downloads_data = []

        for items in download_items:
            for link in items.find_all('a'):
                title = link.text.strip()
                href = link.get('href').strip()
                full_link = "https://www.egerton.ac.ke" + href
                file_format = os.path.splitext(href)[1]

                downloads_data.append({
                    'Title': title,
                    'Link': full_link,
                    'Format': file_format
                })
        return downloads_data
    downloads_data = downloads()    
    downloads_df = pd.DataFrame(downloads_data)
    cur.execute("DROP TABLE IF EXISTS downloads")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Link TEXT,
            Format TEXT
        )
    ''')
    downloads_df.to_sql('downloads', conn, if_exists='append', index=False)


    # notices section
    def notice_board():
        url = "https://www.egerton.ac.ke/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

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


        # Noticeboard link
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

                notice_titles.append(title)
                notice_dates.append(date)
                notice_texts.append(text)

            noticeboard_df = pd.DataFrame({
                'Title': notice_titles,
                'Date': notice_dates,
                'Article': notice_texts
            })
            cur.execute("DROP TABLE notice_board_news")
            cur.execute('''
              CREATE TABLE IF NOT EXISTS notice_board_news (
                  id INTEGER PRIMARY KEY,
                  Title TEXT,
                  Date CHAR(50),
                  Article TEXT,
                  UNIQUE ( id, Title, Date, Article) ON CONFLICT IGNORE
              )
            ''')

            # Save noticeboard data to the database
            noticeboard_df.to_sql('notice_board_news', conn, if_exists='append', index=False)


    recent_news()
    news_data = news("https://www.egerton.ac.ke/news")
    news_df = pd.DataFrame(news_data)
    cur.execute("DROP TABLE egerton_news")
    cur.execute('''CREATE TABLE IF NOT EXISTS egerton_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT,
                    Intro TEXT,
                    Image_url TEXT,
                    Link TEXT,
                    Date CHAR(50),
                    UpdatedDate TIMESTAMP,
                    UNIQUE(id, Title, Intro, Image_url, Link, Date, UpdatedDate) ON CONFLICT IGNORE
                   )''')
    news_df.to_sql('egerton_news', conn, if_exists='append', index=False)
    notice_board()

    conn.commit()
    conn.close()
scraper()
#schedule.every(1).minutes.do(scraper)
#while True:
 #   schedule.run_pending()
  #  time.sleep(20)


