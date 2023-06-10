from timeit import timeit
from math import floor
import sys
from os import sep, remove
from os import path as os_path
import requests
import pandas as pd
import matplotlib.pyplot as plt
#import numpy as np
#import weakref

import common.plotting as plotting
import common.latest_data as latest_data

import warnings
warnings.filterwarnings("ignore")

nsw_url = r'https://data.nsw.gov.au/data/api/3/action/datastore_search?resource_id='
endpoint = r'5d63b527-e2b8-4c42-ad6f-677f14433520'

out_dir = sep.join(os_path.realpath(__file__).split(sep)[0:-1] + ['output'])
csv_path = os_path.join(out_dir, 'nsw_health_master.csv') # raw data
dates_cases_path = os_path.join(out_dir, 'dates_cases.csv') # just dates and cases per day

#start_date = '2021-11-01' # removal of restrictions
#start_date = '2022-02-19' # deaths started reporting
#start_date = '2022-10-20' # before previous wave
# 13 may - PCR require GP referral
start_date = '2022-01-20' # rat/pcr started reporting
current_date = str(pd.to_datetime("today").date())

# csv_to_time_series sorts into a time series instead of per case/cluster
def csv_to_time_series():
    nsw_cases = {}
    for index, record in pd.read_csv(filepath_or_buffer=csv_path, index_col=0).iterrows():
        
        pcr_count = 0
        rat_count = 0
        case_count = int(record["confirmed_cases_count"])
        if record["confirmed_by_pcr"] == 'Yes': pcr_count = case_count
        if record["confirmed_by_pcr"] == 'No': rat_count = case_count
            
        if record["notification_date"] not in nsw_cases:
            nsw_cases[record["notification_date"]] = {"total": case_count, "pcr": pcr_count, "rat": rat_count, "postcodes": {}}
        else:
            nsw_cases[record["notification_date"]]["total"] += case_count
            nsw_cases[record["notification_date"]]["pcr"] += pcr_count
            nsw_cases[record["notification_date"]]["rat"] += rat_count

        if record["postcode"] not in nsw_cases[record["notification_date"]]["postcodes"]:
            nsw_cases[record["notification_date"]]["postcodes"][record["postcode"]] = {"total": case_count, "pcr": pcr_count, "rat": rat_count}
        else:
            nsw_cases[record["notification_date"]]["postcodes"][record["postcode"]]["total"] += case_count
            nsw_cases[record["notification_date"]]["postcodes"][record["postcode"]]["pcr"] += pcr_count
            nsw_cases[record["notification_date"]]["postcodes"][record["postcode"]]["rat"] += rat_count

    dates = list(nsw_cases.keys())
    pd_cases = pd.DataFrame({
         "date": dates,
         "confirm": [nsw_cases[date]["total"] for date in dates]}).set_index("date")
    pd_cases.index = pd.DatetimeIndex(pd_cases.index)
    idx = pd.date_range(dates[0], dates[-1])
    pd_cases = pd_cases.reindex(idx, fill_value=0) # insert empty days
    pd_cases.index.name='date'
    pd_cases.to_csv(path_or_buf=dates_cases_path)

# average and plot subsections
def filter_time_series_and_plot():
    pd_cases = pd.read_csv(filepath_or_buffer=dates_cases_path, index_col='date', parse_dates=True)
    start_date_split = "".join(start_date.split("-"))
    end_date_split = "".join(current_date.split("-"))
    filename = start_date_split + '-' + end_date_split
    pd_cases_trunc = pd_cases.loc[pd.to_datetime(start_date):pd.to_datetime(current_date)]
    pd_cases_trunc.to_csv(path_or_buf=os_path.join(out_dir, f"{filename}.csv"))
    avg = pd_cases_trunc.rolling(window=7).mean().dropna()
    avg['confirm'] = avg['confirm'].astype(int)
    avg.to_csv(path_or_buf=os_path.join(out_dir, f"{filename}_avg.csv"))
    plotting.generate_plots(pd_cases_trunc, avg, filename)
    plotting.generate_plots_log_normal(pd_cases_trunc, avg, filename)

class NSW_Health_API:
    nsw_url = nsw_url
    endpoint = endpoint
    url = nsw_url + endpoint
    
    def __del__(self):
        self.session.close()

    # update master csv with new records
    def update_cases(self):
        iterations = []
        if (self.limit < self.total_records - self.last_numbers):
            batch = floor(self.total_records / self.limit)
            iterations = [self.limit for it in range(0, batch)]
            if (self.total_records - self.last_numbers) - batch * self.limit:
                iterations.append(self.total_records - batch * self.limit)
        else:
            iterations = [self.total_records]
        self.cases = []
        offset = self.last_numbers
        for i in iterations:
            res = self.session.get(f"{self.url}&limit={i}&offset={offset}").json()["result"]["records"]
            for record in res:
                self.cases.append(record)
            offset += i
        latest = pd.DataFrame.from_dict(self.cases)

        # offset the newly recieved records index by how many we already had
        if self.last_numbers:
            latest.index += self.last_numbers
        else:
            # if last numbers is zero we are getting all historical data in bulk so might as well delete whatever csv is there
            if os_path.exists(csv_path):
                remove(csv_path)
        latest.to_csv(path_or_buf=csv_path, mode='a', header=False if os_path.exists(csv_path) else True)
        latest_data.put('nsw_api_records', str(self.total_records))

    # checks connection is ok, sets up a REST connection pool and gets the number of new records available to be retrieved
    def __init__(self):
        try:
            requests.head(self.url)
            self.today = f"{''.join(str(pd.to_datetime('today').normalize().date()).split('-'))}"
            print("running nsw_api " + self.today)
        except requests.exceptions.RequestException as e:  # no raise_for_status() i.e auth error test
            raise SystemExit(e)

        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=100)
        self.session.mount(self.url, adapter)

        res = self.session.get(self.url + "&limit=0").json()
        self.total_records = res["result"]["total"]
        self.last_numbers = int(latest_data.get('nsw_api_records'))
        new_cases = self.total_records - self.last_numbers

        if new_cases:
            print(f"NSW api: {new_cases} new cases")
            res = self.session.get(f"{self.url}&limit={self.total_records}").json()
            self.limit = res["result"]["limit"]
            self.update_cases()
            csv_to_time_series()
            filter_time_series_and_plot()
            sys.exit(0)

def main():
    NSW_Health_API()

if __name__ == "__main__":
    result = timeit(stmt=f"main()", globals=globals(), number=1)
    print(f"Execution time is {result / 1} seconds")