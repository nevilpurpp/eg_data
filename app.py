from flask import Flask, jsonify
from supabase import create_client, Client
import os
from scraper import supabase_client


app = Flask(__name__)
application = app

# Route to access news
@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        response = supabase.table("egerton_news").select("*").execute()
        news = [
            {
                'id': row['id'],
                'Title': row['Title'],
                'Intro': row['Intro'],
                'Image_url': row['Image_url'],
                'Link': row['Link'],
                'Date': row['Date']
            }
            for row in response.data
        ]
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to access recent news
@app.route('/api/recent_news', methods=['GET'])
def get_recent_news():
    try:
        response = supabase.table("recent_egerton_news").select("*").execute()
        recent_news = [
            {
                'id': row['id'],
                'Title': row['Title'],
                'Link': row['Link'],
                'Image_url': row['Image_url'],
                'Date': row['Date']
            }
            for row in response.data
        ]
        return jsonify(recent_news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to access noticeboard
@app.route('/api/noticeboard', methods=['GET'])
def get_noticeboard():
    try:
        response = supabase.table("notice_board_news").select("*").execute()
        noticeboard = [
            {
                'id': row['id'],
                'Title': row['Title'],
                'Date': row['Date'],
                'Article': row['Article']
            }
            for row in response.data
        ]
        return jsonify(noticeboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to access download links
@app.route('/api/download_links', methods=['GET'])
def get_download_links():
    try:
        response = supabase.table("downloads").select("*").execute()
        downloads = [
            {
                'id': row['id'],
                'Title': row['Title'],
                'Link': row['Link'],
                'Format': row['Format']
            }
            for row in response.data
        ]
        return jsonify(downloads)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to send recent news notifications
@app.route('/api/send_recent_news', methods=['POST'])
def trigger_notification():
    
    return jsonify({'message': 'Notification sent successfully'})

# Default route
@app.route('/')
def index():
    return '<h1>Welcome to the Egerton University API</h1>'

if __name__ == '__main__':
   
    app.run()
