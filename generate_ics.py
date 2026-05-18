import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime
import uuid
import pytz
import requests
import yaml
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import os

with open("conifg.yaml", "r", encoding="UTF-8") as yf:
    config = yaml.safe_load(yf)
credentials = HTTPBasicAuth(config["credentials"]["user"], config["credentials"]["password"])

url = "https://planzajec.uek.krakow.pl/index.php?typ=G&id=252681&okres=2"
response = requests.get(url, auth=credentials)
response.encoding = "UTF-8"
page_dom = BeautifulSoup(response.text, "html.parser")

groupe = page_dom.select_one("div.grupa").get_text(strip=True)

classes_tag = page_dom.select_one("table")
with open("temp.html", "w", encoding="UTF-8") as hf:
    hf.write(classes_tag.prettify())
raw = pd.read_html("temp.html", encoding="UTF-8", header=0)[0]
os.remove("temp.html")

raw = raw.loc[raw["Typ"].isin(["ćwiczenia", "wykład", "egzamin"])]
raw[["Day", "Start time", "hyphen", "End time", "Duration"]] = raw["Dzień, godzina"].str.split(" ", expand=True)
raw = raw.drop(["Dzień, godzina", "hyphen", "Duration"], axis=1)

tz = pytz.timezone("Europe/Warsaw")
cal = Calendar()
cal.add("prodid", "-//Apollo Scraper//PL")
cal.add("version", "2.0")

for _, row in raw.iterrows():
    event = Event()
    date = datetime.strptime(str(row["Termin"]), "%Y-%m-%d").date()
    dtstart = tz.localize(datetime.combine(date, datetime.strptime(row["Start time"], "%H:%M").time()))
    dtend   = tz.localize(datetime.combine(date, datetime.strptime(row["End time"],   "%H:%M").time()))

    event.add("uid",         str(uuid.uuid4()))
    event.add("summary",     row.get("Przedmiot", "Zajęcia"))
    event.add("dtstart",     dtstart)
    event.add("dtend",       dtend)
    event.add("location",    row.get("Sala", ""))
    event.add("description", f"Typ: {row.get('Typ', '')}\nNauczyciel: {row.get('Nauczyciel', '')}")
    cal.add_component(event)

with open(f"schedules/{groupe}.ics", "wb") as f:
    f.write(cal.to_ical())

print(f"Done → schedules/{groupe}.ics")