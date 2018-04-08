import requests
import json
import pyperclip
import pprint
import sqlite3
# url = r'http://v.shashkovs.ru/findmespot/?'
# rq = requests.get(url)
# data_json = rq.content.decode('utf-8')
# data = json.loads(data_json)
# pyperclip.copy(pprint.pformat(data))
# messages = data['response']['feedMessageResponse']['messages']['message']


def create_base(path):
    f = open(r''+path, 'w+')
    f.close()
    conn = sqlite3.connect(r''+path)
    c = conn.cursor()
    c.execute('''CREATE TABLE поездки
              (id, name, date_s, date_e, key)''')
    c.execute('''CREATE TABLE точки
                (id, id_trip, id_fms, lat, lons, ts)''')
    conn.commit()
    conn.close()


key, path = map(str, input().split())
try:
    conn = sqlite3.connect(r''+path)
except:
    create_base(path)
    conn = sqlite3.connect(r''+path)
c = conn.cursor()
# код
conn.commit()
conn.close()
