import requests
import json
# import pyperclip
import pprint
import sqlite3
import datetime
from time import strftime
ZERO_TS = datetime.datetime(1, 1, 1, 0, 0)


def create_base(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE trips
              (id int, name text, date_s timestamp, date_e timestamp, key text)''')
    c.execute('''CREATE TABLE waypoints
                (id int, id_trip int, id_fms text, lat float, long float, ts timestamp)''')
    conn.commit()
    conn.close()


def create_dummy_data(path='dummy.db'):
    import random
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(f"""insert into trips values (0, 'trip', '2018-04-01 00:00:00', '2018-06-01 00:00:00', 'aeaeaeaeaeaeaea') """)
    c.execute(f"""insert into trips values (2, 'trip2', '2018-04-02 00:00:00', '2018-06-02 00:00:00', 'aeaeaeaeaeaeaea2') """)
    c.execute(f"""insert into trips values (3, 'trip3', '2018-04-03 00:00:00', '2018-06-03 00:00:00', 'aeaeaeaeaeaeaea3') """)
    c.execute(f"""insert into trips values (4, 'trip4', '2018-04-04 00:00:00', '2018-06-04 00:00:00', 'aeaeaeaeaeaeaea4') """)
    c.execute(f"""insert into trips values (5, 'trip5', '2018-04-05 00:00:00', '2018-06-05 00:00:00', 'aeaeaeaeaeaeaea5') """)

    for id_trip in (0,2,3,4,5):
        for point_num in range(random.randint(0, 100)):
            id_fms = f'{id_trip:04}_{point_num:04}'
            lat = random.random()*90
            long = random.random()*90
            ts = datetime.datetime(2018, 4, 1, 0, 0, 0) + datetime.timedelta(hours=point_num) + datetime.timedelta(days=id_trip)
            c.execute(f"""insert into waypoints values (?, ?, ?, ?, ?, ?) """,
                      (point_num, id_trip, id_fms, lat, long, ts))
    ar2 = c.execute('''select * from waypoints''').fetchall()
    print(ar2)
    conn.commit()
    conn.close()



def fetch_from_findmespot():
    pass
    # url = r'http://v.shashkovs.ru/findmespot/?'
    # rq = requests.get(url)
    # data_json = rq.content.decode('utf-8')
    # data = json.loads(data_json)
    # pyperclip.copy(pprint.pformat(data))
    # messages = data['response']['feedMessageResponse']['messages']['message']


def last_waypoint_time(key, path):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        id_trip = c.execute("SELECT max(id) FROM trips WHERE key = ?", (key, )).fetchall()
        if not id_trip:
            return ZERO_TS
        id_trip = id_trip[0][0]
        last_ts = c.execute("SELECT max(ts) FROM waypoints WHERE id_trip = ?", (id_trip, )).fetchall()
        if not last_ts:
            return ZERO_TS
        return last_ts[0][0]


def main():
    # key, path = map(str, input().split())
    key = 'aeaeaeaeaeaeaea'
    path = 'dummy.db'
    try:
        conn = sqlite3.connect(r''+path)
    except:
        create_base(path)
        conn = sqlite3.connect(r''+path)
    c = conn.cursor()
    last_waypoint = last_waypoint_time(key, path)
    print(last_waypoint)
    # код
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
