from flask import Flask, jsonify
from scraper import db_connection


app = Flask(__name__)


# Route to access news data
@app.route('/api/news', methods=['GET'])
def get_news():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM egerton_news")
    rows = cur.fetchall()

    # list of dictionaries to return as JSON
    news = []
    for row in rows:
        news.append({
            'id': row[0],
            'Title': row[1],
            'Image_url': row[2],
            'Link': row[3],
            'Date': row[4]
        })

    conn.close()
    return jsonify(news)


# Route to access quick links data
@app.route('/api/quick-links', methods=['GET'])
def get_quick_links():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM quick_links")
    rows = cur.fetchall()

    # Create a list of dictionaries to return as JSON
    quick_links = []
    for row in rows:
        quick_links.append({
            'id': row[0],
            'Title': row[1],
            'Link': row[2]
        })

    conn.close()
    return jsonify(quick_links)



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


# Default route
@app.route('/')
def index():
    return '<h1>Welcome to the Egerton University API</h1>'


if __name__ == '__main__':
    app.run(debug=True)
