import urllib.request
import json
import timeit
from math import floor
import weakref

import httpx  # pip install httpx[http2]
import urllib3
import requests


start_date = '2021-11-01'
end_date = '2023-04-24'

tests = [
    'urllib',
    'requests',
    'httpx',
    'httpx_http2_connection_pool',
    'urllib3_connection_pool',
    'requests_connection_pool'
]

class Rest_benchmark:
    nsw_url = r'https://data.nsw.gov.au/data/api/3/action/datastore_search?resource_id='
    endpoint = r'5d63b527-e2b8-4c42-ad6f-677f14433520'
    url = nsw_url + endpoint

    def get_request_test(self, params):

        if self.api == 'urllib': # not actually the get request which is slow, it's the .read() function...
            with urllib.request.urlopen(self.url + params) as response:
                return json.loads(response.read().decode("utf-8"))

        elif self.api == 'requests':
            return requests.get(self.url + params).json()

        elif self.api == 'httpx':
            return httpx.get(self.url + params).json()

        elif self.api == 'httpx_http2_connection_pool':
            return httpx.get(self.url + params).json()

        elif self.api == 'urllib3_connection_pool':
            response = self.urllib3_pool.request('GET', self.url + params)
            return json.loads(response.data.decode('utf-8'))

        elif self.api == 'requests_connection_pool':
            return self.requets_pool.get(self.url + params).json()

    def __del__(self):

        if self.api == 'requests':
            requests.session().close()

        elif self.api == 'httpx_http2_connection_pool':
            self.httpx_http2.close()

        elif self.api == 'urllib3_connection_pool':
            return self.urllib3_pool.clear()

        elif self.api == 'requests_connection_pool':
            return self.requets_pool.close()

    def __init__(self, api='requests', test_mode='batch'):

        self.api = api

        try:
            requests.head(self.url)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        ##### SETUP ########

        if api == 'httpx_http2_connection_pool':
            self.httpx_http2 = httpx.Client(http1=False, http2=True)

        elif api == 'urllib3_connection_pool':
            self.urllib3_pool = urllib3.PoolManager(num_pools=10, maxsize=100)
            #urllib3_pool = urllib3.HTTPConnectionPool(self.nsw_host, maxsize=100, retries=50, timeout=5)

        elif api == 'requests_connection_pool':
            self.requets_pool = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=100)
            self.requets_pool.mount(self.url, adapter)

        iterations = []
        res = requests.get(self.url + "&limit=0").json()
        total_records = res["result"]["total"]
        res = requests.get(self.url + f"&limit={total_records}").json()
        limit = res["result"]["limit"]
        if (limit < total_records):
            batch = floor(total_records / limit)
            iterations = [limit for it in range(0, batch)]
            iterations.append(total_records - batch * limit)
        else:
            iterations = [total_records]

        ##### TEST #####

        if test_mode != 'batch':
            iterations = range(total_records)

        offset = 0
        if test_mode != 'batch':
            offset = 1

        data = []
        for i in iterations:
            if test_mode == 'batch':
                res_dict = self.get_request_test(f"&limit={i}&offset={offset}")["result"]["records"]
                for item in res_dict:
                    data.append(item)
            else:
                res_dict = self.get_request_test(f"&limit={i}&offset={offset}")["result"]["records"]
                for item in res_dict:
                    data.append(item)

            if test_mode == 'batch':
                offset += i

def test(api='requests'):
    test_str = f"weakref.proxy(Rest_benchmark(api='{api}'))"
    result = timeit.timeit(stmt=test_str, globals=globals(), number=1)
    print(f"Execution time for {api} is {result / 1} seconds")
    return result / 1

    # test_str = f"weakref.proxy(Rest_benchmark(api='{api}', test_mode='not_batch'))"
    # result = timeit.timeit(stmt=test_str, globals=globals(), number=1)
    # print(f"Execution time for {api} is {result / 1} seconds")

def main():
    results = []
    for api in tests:
        time = test(api)
        results.append({'name':api, 'time':time})

    tests_sorted = sorted(results, key = lambda d: d['time'])

    print('')

    for api_test in tests_sorted:
        print(api_test['name'], api_test['time'])

if __name__ == "__main__":
    main()