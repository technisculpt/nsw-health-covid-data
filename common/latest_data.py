from os import path as os_path, sep
from sys import path as sys_path
import json
from time import sleep

latest_info = sep.join(os_path.realpath(__file__).split(sep)[0:-2] + ['common', 'latest.json'])

def put(key, val):
    with open(latest_info, 'r+') as f:
        latest = json.load(f)
        latest[key] =  val
        f.seek(0)
        json.dump(latest, f)
        f.truncate()
        return latest

def get(key):
    with open(latest_info, 'r+') as f:
        latest = json.load(f)[key]
        return latest
                
if __name__ == '__main__':
    key = 'nsw_pdf'
    print(get(key))