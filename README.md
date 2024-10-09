# Bluesky bot

## Setup

### Install python 3
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

### Start & activate venv
```bash
cd /home/freebox/bsky
python3 -m venv myenv
source /home/freebox/bsky/myenv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Cron
Make sure you're on the good timezone:
```bash
sudo timedatectl set-timezone <your_timezone>
```
Edit the crontab:
```bash
crontab -e
```

Add the following cron jobs:
```bash
# Run at 10 AM / 10:00 every day with REPOST, saving log with date
0 10 * * * cd /home/freebox/bsky && /home/freebox/bsky/myenv/bin/python dailyLauncher.py REPOST >> /home/freebox/bsky/logs/dailyLogs_$(date +\%Y-\%m-\%d).log 2>&1

# Run at 6 PM / 18:00 every day with IMAGE, saving log with date
0 18 * * * cd /home/freebox/bsky && /home/freebox/bsky/myenv/bin/python dailyLauncher.py IMAGE >> /home/freebox/bsky/logs/dailyLogs_$(date +\%Y-\%m-\%d).log 2>&1

# Run at 8 PM / 20:00 every day to send mails
0 20 * * * cd /home/freebox/bsky && /home/freebox/bsky/myenv/bin/python dailyMail.py >> /home/freebox/bsky/logs/dailyMailLogs_$(date +\%Y-\%m-\%d).log 2>&1
```

Then exit (CTRL + X) and save (Y and Enter)

## Directory Structure
### Setup
```bash
mkdir -p /home/freebox/bsky/logs
```

### Example
```plaintext
/home/bsky
├── dailyChara
│   └── characterName
│        └── data
│            └── 1.png
│            └── ...
│        └── data_to_send.csv
│
├── logs
│   └── dailyLogs_2024-09-10.log
│   └── dailyMailLogs_2024-09-10.log
│
├── myenv
│   └── bin
│   └── ...
│
├── dailyConfig.py
├── dailyGeneric.py
├── dailyLauncher.py
├── dailyMail.py
├── requirements.txt
└── README.md
```