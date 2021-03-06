import os
import sqlite3
from typing import List, Dict
from time_functions import *

APP_PATH = os.path.dirname(os.path.realpath(__file__))
sqlite_db_path = os.path.join(APP_PATH, 'db', 'tracks_prod.db')
DB_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def set_db_path(db_path):
    global sqlite_db_path
    sqlite_db_path = db_path
    print(f'sqlite_db_path = {sqlite_db_path!r}')


def check_base():
    if not os.path.isfile(sqlite_db_path):
        _create_base()


def _create_base():
    with sqlite3.connect(sqlite_db_path) as conn:
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


def get_trip_attributes(fms_key_id: int):
    with sqlite3.connect(sqlite_db_path) as conn:
        c = conn.cursor()
        row = c.execute("""SELECT fms_key, last_waypoint_ts, last_rqs_ts FROM findmespot_keys WHERE fms_key_id = ?""", (fms_key_id,)).fetchall()
    key, last_point_ts, last_rqs_t = row[0]
    last_point_ts = str_ts_to_UTC_ts(last_point_ts)
    last_rqs_t = str_ts_to_UTC_ts(last_rqs_t)
    return key, last_point_ts, last_rqs_t


def all_current_trips():
    with sqlite3.connect(sqlite_db_path) as conn:
        c = conn.cursor()
        c.execute("""SELECT distinct fms_key_id FROM trips WHERE date_e >= ?""", (UTC_ts_to_str_ts(now_time_utc()),))
        return c.fetchall()


def write_waypoints_to_db(messages: List[Dict], key: str):
    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        fms_key_id_rows = cursor.execute("SELECT fms_key_id FROM findmespot_keys where fms_key = ?", (key,)).fetchall()
        if not fms_key_id_rows:
            raise Exception('Findmespot key not found in findmespot_keys')
        fms_key_id = fms_key_id_rows[0][0]
        cursor.execute("UPDATE findmespot_keys SET last_rqs_ts = ? where fms_key_id = ?", (UTC_ts_to_str_ts(now_time_utc()), fms_key_id))
        conn.commit()
        if not messages:
            return
        # Порядок ключей важен! Он должен соответствовать столбцам базы
        waypoints = [
            {
                'fms_key_id': fms_key_id,
                'id_from_fms': waypoint['id'],
                'lat': waypoint['latitude'],
                'long': waypoint['longitude'],
                'alt': waypoint['altitude'],
                'ts': str_ts_to_UTC_ts(waypoint['dateTime']),
                'batteryState': waypoint['batteryState'],
                'msg': waypoint.get('messageContent', ''),
            }
            for waypoint in messages
        ]
        waypoints.sort(key=lambda waypoint: waypoint['ts'])
        fields = ', '.join(waypoints[0].keys())
        placemarks = ', '.join('?'*len(waypoints[0]))
        for waypoint in waypoints:
            waypoint['ts'] = UTC_ts_to_str_ts(waypoint['ts'])
            cursor.execute(f"""INSERT into waypoints ({fields})
                              VALUES ({placemarks})""",
                           tuple(waypoint.values()))
        conn.commit()
        if waypoints:
            cursor.execute("UPDATE findmespot_keys SET last_waypoint_ts = ? where fms_key_id = ?",
                           (waypoints[-1]['ts'], fms_key_id))
        conn.commit()


def get_waypoints_by_trip(trip_name: str):
    with sqlite3.connect(sqlite_db_path) as con:
        cur = con.cursor()
        waypoints = cur.execute('''SELECT waypoints.* FROM waypoints 
                                   join trips on waypoints.fms_key_id = trips.fms_key_id 
                                   where trips.name = ? 
                                   and waypoints.ts between trips.date_s and trips.date_e
                                   ORDER BY waypoints.ts''',
                                (trip_name,)).fetchall()
    return waypoints


def get_nakarte_url_by_trip(trip_name: str) -> str:
    with sqlite3.connect(sqlite_db_path) as con:
        cur = con.cursor()
        nakarte_url = cur.execute('''SELECT nakarte_url FROM trips 
                                   where trips.name = ? 
                                   ''',
                                (trip_name,)).fetchone()
        print('db nakarte_url', nakarte_url)
    if nakarte_url and nakarte_url[0]:
        return nakarte_url[0]
    else:
        return ''


def create_new_trip(trip_name: str, fms_trip_id: str, date_start: datetime, date_end: datetime):
    with sqlite3.connect(sqlite_db_path) as con:
        date_start = UTC_ts_to_str_ts(date_start)
        date_end = UTC_ts_to_str_ts(date_end)
        cur = con.cursor()
        cur.execute('''INSERT INTO findmespot_keys (fms_key, last_rqs_ts, last_waypoint_ts) VALUES (?, ?, ?)''',
                    (str(fms_trip_id), date_start, date_end))
        db_id = cur.execute('''SELECT fms_key_id from findmespot_keys where fms_key = ?''',
                            (str(fms_trip_id),)).fetchall()[0][0]
        cur.execute('''INSERT INTO trips VALUES (?, ?, ?, ?)''',
                    (str(trip_name), date_start, date_end, int(db_id)))
        con.commit()
