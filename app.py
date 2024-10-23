from flask import Flask, jsonify
from scraper import db_connection
from fcm_server import trigger_new_notification
import os


app = Flask(__name__)
application = app

#route to access news
@app.route('/api/news', methods=['GET'])
def get_news():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM egerton_news")
    rows = cur.fetchall()


    news = []
    for row in rows:
        news.append({
            'id': row[0],
            'Title': row[1],
            'Intro': row[2],
            'Image_url': row[3],
            'Link': row[4],
            'Date': row[5]
        })
    conn.close()
    return jsonify(news)    



# Route to access recent news
@app.route('/api/recent_news', methods=['GET'])
def get_recent_news():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM recent_egerton_news")
    rows = cur.fetchall()

    
    recent_news = []
    for row in rows:
        recent_news.append({
            'id': row[0],
            'Title': row[1],
            'Link': row[3],
            'Image_url': row[2],
            'Date': row[4]
        })

    conn.close()
    return jsonify(recent_news)



#route to access noticeboard

@app.route('/api/noticeboard', methods=['GET'])
def get_noticeboard():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notice_board_news")
    rows = cur.fetchall()


    noticeboard = []
    for row in rows:
        noticeboard.append({
            'id': row[0],
            'Title': row[1],
            'Date': row[2],
            'Article': row[3]
        })

    conn.close()
    return jsonify(noticeboard)

# Todo:: route to access download links
#@app.route('/api/download-links')

@app.route('/api/send_recent_news', methods=['POST'])
def trigger_notification():
    send_recent_news_notification()
    return jsonify({'message': 'Notification sent successfully'})

# Default route
@app.route('/')
def index():
    return '<h1>Welcome to the Egerton University API</h1>'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)

