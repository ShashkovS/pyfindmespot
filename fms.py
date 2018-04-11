import requests
import json
import pyperclip
import pprint
import sqlite3
import datetime
from time import strftime, time
import os


NOW_TIME = '2018-06-01 00:00:00'
ZERO_TS = datetime.datetime(1, 1, 1, 0, 0)
DB_DEFAULT_PATH = 'db/tracks.db'


def create_base(path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS trips (name text, date_s timestamp, date_e timestamp, fms_key_id text)""")
        c.execute("""CREATE INDEX IF NOT EXISTS trips_by_name on trips (fms_key_id)""")
        c.execute("""CREATE TABLE IF NOT EXISTS findmespot_keys (fms_key_id text, fms_key text, last_rqs_ts timestamp, last_waypoint_ts timestamp)""")
        c.execute("""CREATE INDEX IF NOT EXISTS findmespot_keys_by_last_rqs_ts on findmespot_keys (last_rqs_ts)""")
        c.execute("""CREATE INDEX IF NOT EXISTS findmespot_keys_by_last_waypoints_ts on findmespot_keys (last_waypoint_ts)""")
        c.execute("""CREATE TABLE IF NOT EXISTS waypoints (id int, fms_key_id text, id_fms text, lat float, long float, alt float, ts timestamp, batteryState text, msg text)""")
        c.execute("""CREATE INDEX IF NOT EXISTS waypoints_by_id_trip on waypoints (fms_key_id)""")
        conn.commit()


def _create_dummy_data(path=DB_DEFAULT_PATH):
    import random
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute(f"""insert into trips values ('trip1', '2018-04-01 00:00:00', '2018-06-01 00:00:00', 'keykey1') """)
        c.execute(f"""insert into trips values ('trip2', '2018-04-02 00:00:00', '2018-06-02 00:00:00', 'keykey2') """)
        c.execute(f"""insert into trips values ('trip3', '2018-04-03 00:00:00', '2018-06-03 00:00:00', 'keykey3') """)
        c.execute(f"""insert into trips values ('trip4', '2018-04-04 00:00:00', '2018-06-04 00:00:00', 'keykey4') """)
        c.execute(f"""insert into trips values ('trip5', '2018-04-05 00:00:00', '2018-06-05 00:00:00', 'keykey5') """)

        # for id_trip in (0,2,3,4,5):
        #    for point_num in range(random.randint(0, 100)):
        #        id_fms = f'{id_trip:04}_{point_num:04}'
        #        lat = random.random()*90
        #        long = random.random()*90
        #        ts = datetime.datetime(2018, 4, 1, 0, 0, 0) + datetime.timedelta(hours=point_num) + datetime.timedelta(days=id_trip)
        #        c.execute(f"""insert into waypoints values (?, ?, ?, ?, ?, ?, ?) """,
        #                  (point_num, id_trip, id_fms, lat, long, 500, ts))
        id_trip = 0
        c.execute(f"""insert into trips values ('real_trip', '2018-04-05 00:00:00', '2018-06-05 00:00:00', 'real_trip_key') """)
        with open('db/test_track.txt') as f:
            data = f.readlines()
            for point_num, row in enumerate(data):
                id_fms = f'{id_trip:04}_{point_num:04}'
                lat, long, alt, ts = row.split()
                c.execute(f"""insert into waypoints values (?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                          (point_num, id_trip, id_fms, float(lat), float(long), float(alt), datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"), 'GOOd', 'OK'))
        conn.commit()

        ar2 = c.execute("""select * from waypoints""").fetchall()
        
        
create_base()
_create_dummy_data()


def fetch_from_findmespot(key, start_ts=ZERO_TS):
    url = 'https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/' + key + '/message.json'
    rq = requests.get(url)
    data_json = rq.content.decode('utf-8')
    data = json.loads(data_json)
    pyperclip.copy(pprint.pformat(data))
    messages = data['response']['feedMessageResponse']['messages']['message']
    for mess in messages:
        if messages[mess]['dateTime'] > start_ts:  # Ещё будет функция перевода времени.
            alt = messages[mess]['altitude']
            lat = messages[mess]['latitude']
            long = messages[mess]['longitude']
            ts = messages[mess]['dateTime']
            battery_state = messages[mess]['batteryState']
            msg = messages[mess].get('messageContent', '-')
            # код
        else:
            break


#def last_waypoint_time(key, path):
#    with sqlite3.connect(path) as conn:
#        c = conn.cursor()
#        id_trip = c.execute("SELECT id FROM trips WHERE key = ?", (key, )).fetchall()
#        id_trip = id_trip[0][0]
#        if not id_trip and id_trip != 0:
#            return ZERO_TS
#        last_ts = c.execute("SELECT max(ts) FROM waypoints WHERE id_trip = ?", (id_trip, )).fetchall()
#        last_ts = last_ts[0][0]
#        if not last_ts:
#           return ZERO_TS
#        return datetime.datetime.strptime(last_ts, "%Y-%m-%d %H:%M:%S")


def main():
    key = 'real_trip_key'
    path = DB_DEFAULT_PATH
    if not os.path.isfile(path):
        create_base(path)
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key_id FROM trips WHERE date_e >= ?""", (NOW_TIME, ))
        now_fms_keys_id = c.fetchall()
        print(now_fms_keys_id)
        for id in now_fms_keys_id:
            id = id[0]
            print(id)
            c.execute("""SELECT last_rqs_ts, last_waypoint_ts FROM findmespot_keys WHERE fms_key_id = ?""", (id, ))
            print(c.fetchall())
            # код


if __name__ == '__main__':
    main()
