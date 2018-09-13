"""
  Store data
"""

import requests as r
from pymongo import MongoClient
import smtplib
import os
import schedule
import time
from logs import logger

accounts = [
    "2547130",
    "2547133",
    "2547148",
]

app_id=os.environ['APP_ID']
secret=os.environ['SECRET']
mongo_user=os.environ['MONGO_USER']
mongo_password=os.environ['MONGO_PASSWORD']
mongo_uri=os.environ['MONGO_URI']
mongo_db=os.environ['MONGO_DB']
schedule_at=os.environ['SCHEDULE_AT']

uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_uri}/{mongo_db}"

def email(e):
    SERVER = "localhost"
    FROM = "finance@personal.io"
    TO = ["claudio@buildo.io"]
    SUBJECT = "Error importing stuff!"
    TEXT = e

    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail

    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()

def jesus():
    logger.info("start scheduled job")
    try:
        mongo = MongoClient(uri)
        db = mongo["finance"]["finance"]
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
            "App-id": f"{app_id}",
            "Secret": f"{secret}"
        }
        for account in accounts:
            logger.info(f"saving account {repr(account)}")
            result = r.get(
                f"https://www.saltedge.com/api/v4/transactions?account_id={account}",
                headers=headers
            )
            for i in result.json()['data']:
                db.replace_one({'id': i['id']}, i, upsert=True)
        mongo.close()
    except Exception as e:
        logger.error(f"something went really wrong {repr(e)}")
        email(repr(e))

if __name__ == "__main__":
    logger.info("hello world")
    schedule.every().day.at(schedule_at).do(jesus)
    while True:
        schedule.run_pending()
        time.sleep(1)
    