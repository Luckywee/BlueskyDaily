import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from atproto import Client, models

from dailyConfig import ACCOUNTS, EMAIL_ADDRESS, EMAIL_PASSWORD

CSV_PATH = "/data_to_send.csv"
LOGS_DIR = "./logs"

def get_likes_left(client : Client, handle):
    params = models.AppBskyFeedGetActorLikes.Params(
        actor=handle,
        limit=100
    )
    response = client.app.bsky.feed.get_actor_likes(params)
    return len(response.feed)

def get_images_left(file_name):
    nb_img = 0

    with open("./" + file_name + CSV_PATH, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, quotechar='"', skipinitialspace=True)
        next(spamreader)
        for row in spamreader:
            if not bool(int(row[3])):
                nb_img += 1

    return nb_img

def get_followers(profile : models.AppBskyActorDefs.ProfileViewDetailed):
    return profile.followers_count


def get_logs_for_today() -> str:
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    log_file_path = os.path.join(LOGS_DIR, f"dailyLogs_{today_date}.log")
    
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            logs = log_file.read()
            return f"<h3>Logs for Today ({today_date})</h3><div style='font-size: 0.75em'><p>{'</p><p>'.join(logs.splitlines())}</p></div><br>"
    else:
        # If the log file doesn't exist, return a message indicating so
        return f"<h3>No logs found for today ({today_date})</h3><br>"

def create_body_for_mail() -> str:
    body = f"<h2>Here is your daily report for your {len(ACCOUNTS)} BlueSky Daily accounts !</h2><br>"
    for account_name in ACCOUNTS:
        account = ACCOUNTS.get(account_name)
        handle = account["BLUESKY_HANDLE"]

        client = Client()
        profile = client.login(handle, account["BLUESKY_PASSWORD"])

        nb_likes_left = str(get_likes_left(client, handle))
        nb_images_left = str(get_images_left(account["FILE_NAME"]))
        nb_followers = str(get_followers(profile))

        body += f"<h3>Report for <strong>{profile.display_name}</strong></h3>"
        body += f"<img style='height:100px' src='{profile.avatar}'/><br>"
        body += f"Reposts left : {nb_likes_left}<br>"
        body += f"Images left : {nb_images_left}<br>"
        body += f"Total followers : {nb_followers}<br>"

    body += get_logs_for_today()

    return body

def create_email() -> MIMEMultipart:
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = f"Daily Report for BlueSky - {datetime.now().strftime('%Y-%m-%d')}"

    # Email body
    body = create_body_for_mail()
    msg.attach(MIMEText(body, 'html'))

    return msg

# Email setup
def send_email(msg : MIMEMultipart):
    # Send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, text)

def main():
    msg = create_email()
    send_email(msg)

if __name__ == '__main__':
    main()