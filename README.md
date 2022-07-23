Simple python script that scrapes [EMGS](https://visa.educationmalaysia.gov.my/) website for visa tracking updates and sends them to Telegram. Because they do not seem to do any kind of notifications unless you file by yourself.

Usage:
1. Copy `.env.example` to `.env` and fill in your details
2. `pipenv install`
3. Run `pipenv run python check.py` every x minutes with cron.
