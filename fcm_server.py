import firebase_admin
from firebase_admin import credentials, messaging
from scraper import db_connection


cred = credentials.Certificate("egertonapp-firebase-adminsdk-sghjd-ab5f380ca5.json")
firebase_admin.initialize_app(cred)




def trigger_new_notification():
    conn = db_connection()
    cur = conn.cursor()
    
    
    cur.execute("SELECT Title, Intro FROM egerton_news ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    
    if row:
        title, intro = row

        truncated_intro = intro[:100] + '...' if len(intro) > 100 else intro
        
        
        message = messaging.Message(
            data={
                'Title': title,
                'Intro': truncated_intro,
            },
            topic='notify',
        )

        # Send the notification
        response = messaging.send(message)
        print('Successfully sent message:', response)
    else:
        print("No recent news available.")
    
    conn.close()

trigger_new_notification()

