from os import path as os_path
from sys import path as sys_path
import json
from time import sleep

latest_mutex = os_path.join(sys_path[0], 'common', r'latest_mutex.json')
latest_info = os_path.join(sys_path[0], 'common', r'latest.json')

def put(key, val):

    time_out_limit = 20
    while time_out_limit:

        with open(latest_mutex, 'r+') as m_f:

            latest_m = json.load(m_f)
            if latest_m['mutex_lock']:
                sleep(0.3)
                time_out_limit -= 1
                if not time_out_limit:
                    print("timed out trying to open latest.json")

            else:
                latest_m['mutex_lock'] =  True
                m_f.seek(0)
                json.dump(latest_m, m_f)
                m_f.truncate()
                with open(latest_info, 'r+') as f:
                    latest = json.load(f)
                    latest[key] =  val
                    f.seek(0)
                    json.dump(latest, f)
                    f.truncate()
                
                    latest_m['mutex_lock'] =  False
                    m_f.seek(0)
                    json.dump(latest_m, m_f)
                    m_f.truncate()
                    return latest

def get(key):

    time_out_limit = 20
    while time_out_limit:

        with open(latest_mutex, 'r+') as m_f:

            latest_m = json.load(m_f)
            if latest_m['mutex_lock']:
                sleep(0.3)
                time_out_limit -= 1
                if not time_out_limit:
                    print("timed out trying to open latest.json")

            else:
                latest_m['mutex_lock'] =  True
                m_f.seek(0)
                json.dump(latest_m, m_f)
                m_f.truncate()
                with open(latest_info, 'r+') as f:
                    latest = json.load(f)[key]
                    latest_m['mutex_lock'] =  False
                    m_f.seek(0)
                    json.dump(latest_m, m_f)
                    m_f.truncate()
                    return latest
                
if __name__ == '__main__':
    key = 'nsw_pdf'
    print(get(key))