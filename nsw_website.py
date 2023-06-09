import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
import json
import os

url = r'https://www.health.nsw.gov.au/Infectious/covid-19/Pages/stats-nsw.aspx'

try:
    response = requests.head(url)
except requests.exceptions.RequestException as e:
    print('Failed to connect. Error:', str(e))
    exit()

try:
    response = requests.get(url)
except requests.exceptions.RequestException as e:
    print('Failed to retrieve. Error:', str(e))
    exit()

soup = BeautifulSoup(response.content, 'html.parser')

try:
    for tag in soup.find_all('h2'):
        if 'NSW up to' in tag.text:
            date_start_index = tag.text.find('NSW up to') + len('NSW up to ')
            date_string = tag.text[date_start_index:]
            date = parse(date_string)
            break
except Exception as e:
    print('Failed to extract content. Error:', str(e))
    exit()

if os.path.exists('date.json'):
    with open('date.json', 'r') as f:
        stored_date = json.load(f).get('stats-nsw')

    if str(date) == stored_date:
        print('No new cases.')
        exit()

try:
    active_cases_div = soup.find('div', {'class': 'active-cases calloutbox'})
    numbers = active_cases_div.find_all('span', {'class': 'number'})
    hospitalized = numbers[0].text
    icu = numbers[1].text
    lives_lost = numbers[2].text
    hospitalized = int(hospitalized.replace(',', ''))
    icu = int(icu.replace(',', ''))
    lives_lost = int(lives_lost.replace(',', ''))

except Exception as e:
    print('Failed to extract health data. Error:', str(e))
    exit()

print(f"{date = }")
print(f"{hospitalized = }")
print(f"{icu = }")
print(f"{lives_lost = }")

with open('date.json', 'w') as f:
    json.dump({'stats-nsw': str(date)}, f)
