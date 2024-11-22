import requests
from bs4 import BeautifulSoup
import os
import datetime
from supabase import create_client, Client

# Initialize Supabase Client
def supabase_client():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL or Key is missing.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = supabase_client()

# Write to Supabase
def write_to_supabase(table_name, data):
    try:
        response = supabase.table(table_name).insert(data).execute()
        if response.status_code != 201:
            print(f"Error inserting into {table_name}: {response.json()}")
    except Exception as e:
        print(f"Error inserting into {table_name}: {e}")

# Scraper function
def scraper():
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

                    news_data.append({
                        "Title": title,
                        "Link": link,
                        "Image_url": image,
                        "Date": date,
                    })

            
            write_to_supabase("recent_egerton_news", news_data)
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

                    all_news_data.append({
                        "Title": title,
                        "Intro": intro,
                        "Image_url": image,
                        "Link": link,
                        "Date": date,
                        "UpdatedDate": updated_date.isoformat(),
                    })

                current_page += 1
            except requests.RequestException as e:
                print("Error fetching news:", e)
                break

        
        write_to_supabase("egerton_news", all_news_data)

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
                    downloads_data.append({
                        "Title": title,
                        "Link": full_link,
                        "Format": file_format,
                    })

            
            write_to_supabase("downloads", downloads_data)
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
                    notice_data.append({
                        "Title": title,
                        "Date": date,
                        "Article": text,
                    })

                # Write to Supabase
                write_to_supabase("notice_board_news", notice_data)
        except requests.RequestException as e:
            print("Error fetching notice board:", e)

    # Execute functions
    recent_news()
    news("https://www.egerton.ac.ke/news")
    downloads()
    notice_board()

scraper()
