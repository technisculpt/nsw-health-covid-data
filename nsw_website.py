import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
import pandas as pd
import common.latest_data as latest_data

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

date = ''
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

stored_date = latest_data.get('nsw_asp')

if str(date) == stored_date:
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
    print('Failed to extract hospitalized/icu/lives_lost/. Error:', str(e))
    exit()

try:
    cases = ''
    rat_cases = ''
    pcr_cases = ''
    table = soup.find('table', attrs={'class':'moh-rteTable-6 cases'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')[1:2]
    for row in rows:
        cols = row.find_all('td')[1:]
        cols = [ele.text.strip() for ele in cols]
        pcr_cases = int(cols[0].replace(',', ''))
        rat_cases = int(cols[1].replace(',', ''))
        cases = int(cols[2].replace(',', ''))
except Exception as e:
    print('Failed to extract cases/rat_cases/pcr_cases/. Error:', str(e))
    exit()


new_data = {
    "date": date.date(), 
    "deaths": lives_lost, 
    "cases": cases, 
    "hospitalised": hospitalized, 
    "icu": icu, 
    "rat_cases": rat_cases, 
    "pcr_cases": pcr_cases
}

new_row = pd.DataFrame(new_data, index=[0])
new_row.to_csv('output/website.csv', mode='a', header=False, index=False)

latest_data.put('nsw_asp', str(date))

with open(f'output/website/{date.date()}.html', 'w') as f:
    f.write(response.content.decode())