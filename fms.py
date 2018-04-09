import requests
import json
# import pyperclip
import pprint
import sqlite3
import datetime
from time import strftime
import os


ZERO_TS = datetime.datetime(1, 1, 1, 0, 0)
DB_DEFAULT_PATH = 'db/tracks.db'


def create_base(path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE trips (id int, name text, date_s timestamp, date_e timestamp, key text)''')
        c.execute('''CREATE INDEX IF NOT EXISTS trips_by_name on trips (key)''')
        c.execute('''CREATE TABLE waypoints (id int, id_trip int, id_fms text, lat float, long float, ts timestamp)''')
        c.execute('''CREATE INDEX IF NOT EXISTS waypoints_by_id_trip on waypoints (id_trip)''')
        conn.commit()

def _create_dummy_data(path=DB_DEFAULT_PATH):
    import random
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute(f"""insert into trips values (0, 'trip1', '2018-04-01 00:00:00', '2018-06-01 00:00:00', 'keykey1') """)
        c.execute(f"""insert into trips values (2, 'trip2', '2018-04-02 00:00:00', '2018-06-02 00:00:00', 'keykey2') """)
        c.execute(f"""insert into trips values (3, 'trip3', '2018-04-03 00:00:00', '2018-06-03 00:00:00', 'keykey3') """)
        c.execute(f"""insert into trips values (4, 'trip4', '2018-04-04 00:00:00', '2018-06-04 00:00:00', 'keykey4') """)
        c.execute(f"""insert into trips values (5, 'trip5', '2018-04-05 00:00:00', '2018-06-05 00:00:00', 'keykey5') """)

        for id_trip in (0,2,3,4,5):
            for point_num in range(random.randint(0, 100)):
                id_fms = f'{id_trip:04}_{point_num:04}'
                lat = random.random()*90
                long = random.random()*90
                ts = datetime.datetime(2018, 4, 1, 0, 0, 0) + datetime.timedelta(hours=point_num) + datetime.timedelta(days=id_trip)
                c.execute(f"""insert into waypoints values (?, ?, ?, ?, ?, ?) """,
                          (point_num, id_trip, id_fms, lat, long, ts))
        conn.commit()

        ar2 = c.execute('''select * from waypoints''').fetchall()
        print(ar2)


# create_base()
# _create_dummy_data()
# exit()


def fetch_from_findmespot(key, start_ts=ZERO_TS):
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
        return datetime.datetime.strptime(last_ts[0][0], "%Y-%m-%d %H:%M:%S")


def main():
    # key, path = map(str, input().split())
    key = 'keykey2'
    path = DB_DEFAULT_PATH
    if not os.path.isfile(path):
        create_base(path)
    last_waypoint = last_waypoint_time(key, path)
    print(last_waypoint)


if __name__ == '__main__':
    main()
