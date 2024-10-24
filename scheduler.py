import time
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import scraper
from fcm_server import trigger_new_notification
#scheduler set up

scheduler = BackgroundScheduler()
scheduler.add_job(scraper, 'interval', minutes=2)
scheduler.add_job(trigger_new_notification, 'interval', minutes=1)
if __name__ == '__main__':
    try:
        scheduler.start()
        while True:
            time.sleep(2)
    except(keyboardInterrupt, SystemExit):
        scheduler.shutdown()        


