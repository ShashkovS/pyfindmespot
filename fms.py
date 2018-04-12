import requests
import json
import pyperclip
import pprint
import sqlite3
import datetime
from time import strftime, time
import os


NOW_TIME = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
ZERO_TS = datetime.datetime(2000, 1, 1, 0, 0)
DB_DEFAULT_PATH = 'db/tracks.db'
FIND_ME_SPOT_URL = r'https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/{key}/message.json?startDate={startDate}'


def ts_to_UTC_str(ts):
    return (ts + datetime.timedelta(hours=-3)).isoformat(sep='T', timespec='seconds') + '-0000'


def create_base(path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS findmespot_keys (
                         fms_key_id INTEGER PRIMARY KEY, 
                         fms_key text, 
                         last_rqs_ts timestamp, 
                         last_waypoint_ts timestamp
                     )""")
        c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS findmespot_keys_by_fms_key on findmespot_keys (fms_key)""")
        c.execute("""CREATE TABLE IF NOT EXISTS trips (
                         name text PRIMARY KEY, 
                         date_s timestamp,
                         date_e timestamp,
                         fms_key_id int, 
                         FOREIGN KEY(fms_key_id) REFERENCES findmespot_keys(fms_key_id)
                     )""")
        c.execute("""CREATE TABLE IF NOT EXISTS waypoints (
                         waypoint_id INTEGER PRIMARY KEY, 
                         fms_key_id int, 
                         id_from_fms text, 
                         lat float, 
                         long float, 
                         alt float, 
                         ts timestamp, 
                         batteryState text, 
                         msg text,
                         FOREIGN KEY(fms_key_id) REFERENCES findmespot_keys(fms_key_id)
                     )""")
        c.execute("""CREATE INDEX IF NOT EXISTS waypoints_by_fms_key_id on waypoints (fms_key_id)""")
        conn.commit()


def _create_dummy_data(path=DB_DEFAULT_PATH):
    import random
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        for fms_key_id in range(2, 5):
            c.execute(f"""insert into findmespot_keys values ({fms_key_id}, 'asdfsjlibdummy{fms_key_id}', '0001-01-01 00:00:00', '0001-01-01 00:00:00')""")
            c.execute(f"""insert into trips values ('trip{fms_key_id}', '2018-04-0{fms_key_id} 00:00:00', '2018-06-0{fms_key_id} 00:00:00', {fms_key_id}) """)
            for point_num in range(random.randint(0, 100)):
                id_from_fms = f'{fms_key_id:04}_{point_num:04}'
                lat = random.random()*90
                long = random.random()*90
                ts = datetime.datetime(2018, 4, 1, 0, 0, 0) + datetime.timedelta(hours=point_num) + datetime.timedelta(days=fms_key_id)
                batteryState = 'GOOD'
                msg = 'Bce cynep!'
                c.execute(f"""insert into waypoints (fms_key_id, id_from_fms, lat, long, alt, ts, batteryState, msg) 
                              values (?, ?, ?, ?, ?, ?, ?, ?) """,
                          (fms_key_id, id_from_fms, lat, long, 500, ts, batteryState, msg ))
        fms_key_id = 1
        c.execute(f"""insert into findmespot_keys values ({fms_key_id}, '0N0t9EXiJA8115ifa6qTkfqNGgxoCpvla', '0001-01-01 00:00:00', '0001-01-01 00:00:00')""")
        c.execute(f"""insert into trips values ('real_track', '2018-04-0{fms_key_id} 00:00:00', '2018-06-0{fms_key_id} 00:00:00', {fms_key_id}) """)
        with open('db/test_track.txt') as f:
            data = f.readlines()
            for point_num, row in enumerate(data):
                id_from_fms = f'{fms_key_id:04}_{point_num:04}'
                lat, long, alt, ts = row.split()
                batteryState = 'GOOD'
                msg = 'Bce cynep!'
                c.execute(f"""insert into waypoints (fms_key_id, id_from_fms, lat, long, alt, ts, batteryState, msg) 
                              values (?, ?, ?, ?, ?, ?, ?, ?) """,
                          (fms_key_id, id_from_fms, lat, long, 500, ts, batteryState, msg ))
        conn.commit()

        ar2 = c.execute("""select * from waypoints""").fetchall()
        
        
create_base()
_create_dummy_data()
exit()


def updating_tables(messages: dict, key: str, path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        alt = messages['altitude']
        lat = messages['latitude']
        long = messages['longitude']
        ts = messages['dateTime']
        battery_state = messages['batteryState']
        msg = messages.get('messageContent', '-')
        fms_key_id = c.execute("SELECT fms_key_id FROM findmespot_keys where fms_key = ?", (key, )).fetchall()[0]
        id_from_fms = messages['id']
        c.execute(f"""INSERT into waypoints (fms_key_id, id_from_fms, lat, long, alt, ts, batteryState, msg)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (fms_key_id, id_from_fms, lat, long, alt, ts, battery_state, msg))
        c.execute("UPDATE findmespot_keys SET last_waypoint_ts = ? where fms_key_id = ?", (messages['dateTime'], fms_key_id))
        c.execute("UPDATE findmespot_keys SET last_rqs_ts = ? where fms_key_id = ?", (NOW_TIME, fms_key_id))
        conn.commit()


def fetch_from_findmespot(key: str, start_ts=ZERO_TS):
    path = DB_DEFAULT_PATH
    url = FIND_ME_SPOT_URL.format(key=key, startDate=ts_to_UTC_str(ZERO_TS))
    rq = requests.get(url)
    data_json = rq.content.decode('utf-8')
    data = json.loads(data_json)
    pyperclip.copy(pprint.pformat(data))
    messages = data['response']['feedMessageResponse']['messages']['message']
    for mess in messages:
        if messages[mess]['dateTime'] > start_ts:  # Ещё будет функция перевода времени.
            updating_tables(messages[mess], key, path)
        else:
            break


def all_current_trips(path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key_id FROM trips WHERE date_e >= ?""", (NOW_TIME, ))
        return c.fetchall()


def call_fetch_from_fms(path, id):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key, last_waypoint_ts, last_rqs_ts FROM findmespot_keys WHERE fms_key_id = ?""", (id, ))
        key, star_t, last_rqs_t = c.fetchall()
        if datetime.datetime.strptime(last_rqs_t, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=3) <= datetime.datetime.now():
            fetch_from_findmespot(key, star_t)


def main():
    path = DB_DEFAULT_PATH
    if not os.path.isfile(path):
        create_base(path)
        now_fms_keys_id = all_current_trips(path)
        for id in now_fms_keys_id:
            call_fetch_from_fms(path, id[0])


if __name__ == '__main__':
    main()
