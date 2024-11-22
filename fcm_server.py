import firebase_admin
from firebase_admin import credentials, messaging
from supabase import create_client, Client
import os
from scraper import supabase_client

# Initialize Firebase Admin

firebase_credentials = os.getenv("FIREBASE_ADMIN_CREDENTIALS")

if firebase_credentials:
    firebase_credentials_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(firebase_credentials_dict)
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("Firebase credentials are not set in the environment variables")


def trigger_new_notification():
    try:
        # Fetch the most recent news
        response = supabase.table("egerton_news").select(
            "Title, Intro, Image_url, Link"
        ).order("UpdatedDate", desc=True).limit(1).execute()

        if response.data:
            latest_news = response.data[0]  # Get the first record
            title = latest_news['Title']
            intro = latest_news['Intro']
            image = latest_news['Image_url']
            link = latest_news['Link']

            # Truncate the introduction if necessary
            truncated_intro = intro[:150] + '...' if len(intro) > 150 else intro

            # Create the notification message
            message = messaging.Message(
                data={
                    'Title': title,
                    'Intro': truncated_intro,
                    'Image_url': image,
                    'Link': link,
                    'MessageId': '1234'  # Replace with a dynamic ID if needed
                },
                topic='notify',
            )

            # Send the notification
            response = messaging.send(message)
            print('Successfully sent message:', response)
        else:
            print("No recent news available.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Trigger the notification
trigger_new_notification()
