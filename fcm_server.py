import firebase_admin
from firebase_admin import credentials, messaging
from scraper import db_connection
#import schedule
#import time

firebase_credentials_path = "/etc/secrets/egertonapp-firebase-adminsdk-sghjd-ab5f380ca5.json"
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)




def trigger_new_notification():
    conn = db_connection()
    cur = conn.cursor()
    
    
    cur.execute("SELECT Title, Intro, Image_url, Link FROM egerton_news ORDER BY UpdatedDate DESC LIMIT 1")
    row = cur.fetchone()
    
    if row:
        title, intro, image, link = row

        truncated_intro = intro[:150] + '...' if len(intro) > 150 else intro
        
        
        message = messaging.Message(
            data={
                'Title': title,
                'Intro': truncated_intro,
                'Image_url': image,
                'Link': link,
                'MessageId': '1234'  
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
    
#schedule.every(30).minutes.do(trigger_new_notification)
#while True:
 #   schedule.run_pending()
  #  time.sleep(30)


