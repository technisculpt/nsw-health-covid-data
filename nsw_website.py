import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse
import json
import os

# polling website to extracting People in hospital, People in ICU, and lives lost in the past 7 days
# it has worked but is tempermental, work in progress

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
    script_tag = soup.find('script', text=re.compile('clientServerTimeDelta'))
    date_string = re.search(r'new Date\\(\"(.*?)\"\\)', script_tag.string).group(1)
    date = parse(date_string)
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

with open(f'{date}.html', 'w') as f:
    f.write(response.content.decode())
