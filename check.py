import pickle
import requests
from os.path import exists
from bs4 import BeautifulSoup
from pyrogram import Client
import os
import sys
from dotenv import load_dotenv

load_dotenv()

SEARCH_FORM="https://visa.educationmalaysia.gov.my/emgs/application/searchForm/"
SEARCH_POST="https://visa.educationmalaysia.gov.my/emgs/application/searchPost/"
STEPS_COMPARE_FILE="saved_steps"
PASSPORT=os.getenv("PASSPORT")
NATIONALITY=os.getenv("NATIONALITY")
API_ID=int(os.getenv("TG_APP_ID"))
API_HASH=os.getenv("TG_APP_HASH")
API_TOKEN=os.getenv("TG_BOT_TOKEN")
USER=os.getenv("TG_SEND_TO")

def get_steps_and_new_status():
    form_key_req = requests.get(SEARCH_FORM)

    if form_key_req.status_code != 200:
        print(f"Failed to get search form. Status code {form_key_req.status}")
        sys.exit(1)

    key_tag = BeautifulSoup(form_key_req.text, 'html.parser').find("input", {"name": "form_key"})

    if key_tag is None:
        print("Failed to find form key in search form HTML")
        sys.exit(1)

    key = key_tag["value"]

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"form_key": key, "nationality": NATIONALITY, "travel_doc_no": PASSPORT, "type": "visa", "agreement": 1}
    results_req = requests.post(SEARCH_POST, data=data, headers=headers, cookies=form_key_req.cookies)

    if results_req.status_code != 200:
        print(f"Failed to get search results. Status code {form_key_req.status}")
        sys.exit(1)

    soup = BeautifulSoup(results_req.text, "html.parser")
    steps = soup.find("table", {"id": "form-table"}).findChildren("tr")[1:]
    percentage_table = soup.find("div", {"id": "accordion1"}).findChildren("td")
    percentage = percentage_table[0].findChild("h2").text.strip()
    percentage_explaination = percentage_table[1].findChild("p").text.strip()

    print(percentage)
    print(percentage_explaination)

    formatted_steps = []
    for step in steps:
        fields = step.findChildren("td")
        date = fields[0].text.strip()
        short_desc = fields[1].text.strip()
        long_desc = fields[2].text.strip()
        formatted_steps.append({"date": date, "short_desc": short_desc, "long_desc": long_desc})
    status = {"percentage": percentage, "explaination": percentage_explaination, "steps": formatted_steps}
    new_flag = True
    if exists(STEPS_COMPARE_FILE):
        with open(STEPS_COMPARE_FILE, "rb") as status_file:
            old_status = pickle.load(status_file)
            if (old_status == status):
                new_flag = False
               
    with open(STEPS_COMPARE_FILE, "wb") as status_file:
        pickle.dump(status, status_file)
    return (new_flag, status)


with Client("my_session", api_id=API_ID, api_hash=API_HASH, bot_token=API_TOKEN) as app:
    (new, status) = get_steps_and_new_status()
    if new:
        print("New updates found")
        message = "New visa update:\n"
        message += f"Percentage: {status['percentage']}\n\n"
        message += f"{status['explaination']}\n\n"
        message += f"History:\n"
        for status in status["steps"]:
            message += status["date"] + ": " + status["short_desc"] + "\n" + status["long_desc"] + "\n\n"
        app.send_message(USER, message)
    else:
        print("No new updates found")
