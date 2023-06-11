# currently not parsing any information, just backing up the pdfs as they become available
# https://www.health.nsw.gov.au/Infectious/covid-19/Pages/weekly-reports.aspx

import pandas as pd
import os
from os import sep, mkdir
from os import path as os_path
from sys import path as sys_path
import requests

from PyPDF2 import PdfReader

from common.plotting import step_plot
import common.latest_data as latest_data

latest_file = r'pdf.json'

pdf_stub = r'weekly-covid-overview-'
base_url = r'https://www.health.nsw.gov.au/Infectious/covid-19/Documents/weekly-covid-overview-'
out_path = sep.join(os_path.realpath(__file__).split(sep)[0:-1] + ['output'])
pdf_path = os_path.join(out_path, 'pdfs')
output_csv = os_path.join(out_path, "pdf_deaths.csv")

def check_for_pdf() -> None:

    today_date = pd.to_datetime("today")
    latest_date = pd.to_datetime(latest_data.get('nsw_pdf'))
    if (today_date - (latest_date + pd.Timedelta(3, "d"))).days  > 6: # report typically published 4-5 days after report ending date
        dates = pd.date_range(start=latest_date + pd.Timedelta(1, "d"), end=today_date, freq='W-SAT', tz='Australia/Sydney', normalize=True)
        
        for date in dates:
            new_date = f"{''.join(str(date.normalize().date()).split('-'))}"
            url = f"{base_url}{new_date}.pdf"
            response = requests.head(url)

            if (response.status_code == 200):

                print(f"Saving PDF from date {new_date}")
                response = requests.get(url)
                with open(f"{pdf_path}{pdf_stub}{new_date}.pdf", 'wb') as f:
                    f.write(response.content)
                latest_data.put('nsw_pdf', new_date)
            
            elif (response.status_code == 404):
                print(f"No PDF on date {new_date}")

            else:
                print(f"Error retrieving PDF for {new_date}: {response.status_code}")

def get_historical_data() -> None:

    start='2022-02-19'
    times = pd.date_range(start=start, end=pd.to_datetime('today'), freq='W-' + pd.to_datetime(start).strftime('%a'), tz='Australia/Sydney', normalize=True)

    if not os_path.exists(pdf_path):
        mkdir(pdf_path)

    date = ''
    for time in times:
        date = f"{''.join(str(time.normalize().date()).split('-'))}"
        url = f"{base_url}{date}.pdf"
        response = requests.head(url)

        if (response.status_code == 200):

            if os_path.isfile(f"{pdf_path}/{pdf_stub}{date}.pdf"):
                print(f"PDF on date {date} already saved")
                continue

            print(f"Saving PDF from date {date}")
            response = requests.get(url)
            with open(f"{pdf_path}/{pdf_stub}{date}.pdf", 'wb') as f:
                f.write(response.content)
        
        elif (response.status_code == 404):
            print(f"No PDF on date {date}")
            
    latest_data.put('nsw_pdf', date)

def parse_stats_v2(nsw_pdf='pdfs/weekly-covid-overview-20230408.pdf') -> list: # or dict?
    
    death_cnt = []
    dates = []
    date = ""

    with open(nsw_pdf, 'rb') as f:

        pdf = PdfReader(f)
        date_str = nsw_pdf.split('-')[-1].split('.')[0]
        date = pd.to_datetime(date_str)
        dates.append(date)

        ### Hospital, ICU and Deaths Table:
        # Table 1 from 20220430 onwards (inclusive)
        # Table 3 on 20220423 including vaccination status (random one off)
        # prior to 20220416 inclusive, deaths of vaccination status a seperate table, Table 2. Deaths by age Table 4
        # on 20220226 (first PDF), Table 4 is vaccination status and Table 3 is Reported deaths

        page_content = pdf.pages[1].extract_text()
        page_content += pdf.pages[2].extract_text()
        page_content += pdf.pages[3].extract_text()
        page_content += pdf.pages[4].extract_text()
        page_lines = page_content.split('\n')
        deaths_found = False
        deaths_index = -1


        if date_str == '20220423':
            for index, line in enumerate(page_lines):
                if line.find("Table") != -1:
                    if not deaths_found:
                        if (   line.find("deaths") != -1
                            or line.find("died") != -1
                            or page_lines[index + 1].find("deaths") != -1 
                            or page_lines[index + 1].find("died") != -1):
                                deaths_found = True
                                deaths_index = index
        
        else:
            for index, line in enumerate(page_lines):
                if line.find("Table") != -1:
                    if ((  line.find("deaths") != -1
                        or line.find("died") != -1
                        or page_lines[index + 1].find("deaths") != -1 
                        or page_lines[index + 1].find("died") != -1)
                        and line.find("vaccination") == -1):
                            deaths_found = True
                            deaths_index = index

        #print(deaths_table)
        deaths_index += 1
        deaths_table = []
        if deaths_found:
            parse_info = True
            while(parse_info):
                new_line = page_lines[deaths_index]
                if (new_line.find("Table") != -1
                    or new_line.find("Despite the") != -1
                    or new_line.find("Communicable") != -1
                    #or new_line.find("Vaccination") != -1
                    or new_line.find("Excludes") != -1):
                    parse_info = False
                    break
                else:
                    deaths_table.append(new_line)
                    deaths_index += 1
        else:
            print(date, "Table 1 not found")

    stats = ['Female', 'Male', 'Transgender', 'described', '0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+',
             'Central Coast', 'Illawarra Shoalhave', 'Nepean Blue Mountains', 'Northern Sydney', 'South Eastern Sydney', 'South Western Sydney',
             'Sydney', 'Western Sydney', 'Far West', 'Hunter New England', 'Mid North Coast', 'Murrumbidgee','Northern NSW''Southern NSW','Western NSW', 'Total']
    
    stats_new = [] # or dict?

    gender = [] #done?
    age = [] #done
    district = [] # done for deaths, could get earlier diagnosis per district
    vaccines = [] #dowecare?
    total = "" #done

    gender_flag = False
    age_flag = False
    district_flag = False
    vaccine_flag = False

    for line in deaths_table:

        if line.find("Total") != -1:
            vaccine_flag = False
            total = line

        if vaccine_flag:
            vaccines.append(line)

        if line.find("Vaccination") != -1:
            vaccine_flag = True
            district_flag = False

        if district_flag:
            district.append(line)

        if line.find("District") != -1 or line.find("Central Coast") != -1: # deaths per district started on 20220423, prior had diagnosis by test per district
            district_flag = True
            if line.find("Central Coast") != -1:
                if date_str == '20220430':
                    index = line.find("Central Coast")
                    district.append(line[index:len(line)])
                else:
                    district.append(line)

        if line.find("0-9") != -1:
            gender_flag = False

        if age_flag:
            new_age_line = ''
            if date_str == '20220430':
                if line.find("Metropolitan Sydney") != -1:
                    index = line.find("Metropolitan Sydney")
                    new_age_line = line[0:index].split(' ')
                elif line.find("0-9") != -1:
                    index = line.find("0-9")
                    new_age_line = line[index:len(line)].split(' ')
                else:
                    new_age_line = line.split(' ')
            else:
                new_age_line = line.split(' ')
            while '' in new_age_line:
                new_age_line.remove('')
            age.append(new_age_line)
            if line.find("90+") != -1:
                age_flag = False

        if gender_flag:
            if line.find('Age') != -1:
                gender_flag = False
            else:
                gender.append(line)

        if line.find("Gender") != -1:
            gender_flag = True

    print(nsw_pdf)
    print(gender)
    print(age)
    print(district)
    print(total)

def parse_stats() -> None: # deaths only. works for up until 20230429

    from PyPDF2 import PdfReader

    death_cnt = []
    dates = []
    date = ""

    for file in [os.path.join(pdf_path, f) for f in os.listdir(pdf_path) if os.path.isfile(os.path.join(pdf_path, f))]:
        with open(file, 'rb') as f:
            pdf = PdfReader(f)
            information = pdf.metadata

            ###### some issue with date in pdf metadata on 1 occasion, use date from get request
            date = pd.to_datetime(file.split('-')[-1].split('.')[0])
            
            #title = information.title # NSW Respiratory Surveillance Report - week ending 01 April 2023  originally NSW COVID-19 WEEKLY DATA OVERVIEW Epidemiological week 12 ending 26 March 2022
            #date = pd.to_datetime(title.split('ending')[1])
            #print(str(date).split(' ')[0], str(date1).split(' ')[0], information.author)
            #if(date != date1):
            #    print(file, date)
            #    print(information)

            dates.append(date)
            page_content = pdf.pages[1].extract_text()
            page_content += pdf.pages[2].extract_text()
            page_content += pdf.pages[3].extract_text()
            page_lines = page_content.split('\n')
            deaths_found = False
            deaths_index = 0
            for index, line in enumerate(page_lines):
                if line.find("Table") != -1:
                    if line.find("deaths") != -1 or line.find("died") != -1:
                        deaths_found = True
                        deaths_index = index
                    else:
                        if page_lines[index + 1].find("deaths") != -1  or page_lines[index + 1].find("died") != -1:
                            deaths_found = True
                            deaths_index = index
            if not deaths_found:
                print(date, "DEATHS NOT FOUND")
            else:
                for index, line in enumerate(page_lines[deaths_index + 1:-1]):
                    if line.find('Total') != -1:
                        death_data = ([val for val in line.split('Total')[1].split(' ') if val != ''])
                        if len(death_data) < 3:
                            death_cnt.append(death_data[0])
                        else:
                            death_cnt.append(death_data[2])
                        break

    death_pd = pd.DataFrame({"deaths": death_cnt, "date": dates}).set_index("date")
    death_pd.to_csv(path_or_buf = output_csv)

def main() -> None:
    #get_historical_data()
    check_for_pdf()
    #parse_stats()
    


if __name__ == '__main__':
    main()