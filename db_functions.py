import os
import sqlite3
from typing import List, Dict

import datetime

ZERO_TS = datetime.datetime(2000, 1, 1, 0, 0).astimezone(datetime.timezone.utc)
sqlite_db_path = r'db/tracks2.db'
DB_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def now_time_utc():
    return datetime.datetime.now().astimezone(datetime.timezone.utc)


def UTC_ts_to_fms_ts(dt):
    return dt.astimezone(datetime.timezone(offset=datetime.timedelta(hours=-8))).strftime("%Y-%m-%dT%H:%M:%S%z")


def fms_ts_to_UTC_ts(ts_utc):
    dt = datetime.datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%S%z")
    return dt.astimezone(datetime.timezone.utc)


def db_ts_to_UTC_ts(ts_utc):
    # dt = datetime.datetime.strptime(ts_utc, "%Y-%m-%d %H:%M:%S%z")
    dt = datetime.datetime.fromisoformat(ts_utc)
    return dt.astimezone(datetime.timezone.utc)



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


def get_trip_attributes(id):
    with sqlite3.connect(sqlite_db_path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key, last_waypoint_ts, last_rqs_ts FROM findmespot_keys WHERE fms_key_id = ?""", (id,))
        return c.fetchall()


def all_current_trips():
    with sqlite3.connect(sqlite_db_path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key_id FROM trips WHERE date_e >= ?""", (now_time_utc(),))
        return c.fetchall()


def write_waypoints_to_db(messages: List[Dict], key: str):
    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        fms_key_id_rows = cursor.execute("SELECT fms_key_id FROM findmespot_keys where fms_key = ?", (key,)).fetchall()
        if not fms_key_id_rows:
            raise Exception('Findmespot key not found in findmespot_keys')
        fms_key_id = fms_key_id_rows[0][0]
        cursor.execute("UPDATE findmespot_keys SET last_rqs_ts = ? where fms_key_id = ?", (now_time_utc(), fms_key_id))
        conn.commit()

        max_ts_seen = ZERO_TS

        for waypoint in messages:
            alt = waypoint['altitude']
            lat = waypoint['latitude']
            long = waypoint['longitude']
            ts = fms_ts_to_UTC_ts(waypoint['dateTime'])
            max_ts_seen = max(ts, max_ts_seen)
            battery_state = waypoint['batteryState']
            msg = waypoint.get('messageContent', '')
            id_from_fms = waypoint['id']
            cursor.execute(f"""INSERT into waypoints (fms_key_id, id_from_fms, lat, long, alt, ts, batteryState, msg)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (fms_key_id, id_from_fms, lat, long, alt, ts, battery_state, msg))
        conn.commit()
        cursor.execute("UPDATE findmespot_keys SET last_waypoint_ts = ? where fms_key_id = ?",
                       (ts, fms_key_id))
        conn.commit()


def get_waypoints_by_trip(trip_name: str):
    with sqlite3.connect(sqlite_db_path) as con:
        cur = con.cursor()
        waypoints = cur.execute('''SELECT waypoints.* FROM waypoints 
                                   join trips on waypoints.fms_key_id = trips.fms_key_id
                                   where trips.name = ?''',
                                (trip_name,)).fetchall()
    return waypoints


def create_new_trip(trip_name: str, fms_trip_id: str, date_start: datetime.datetime, date_end: datetime.datetime):
    with sqlite3.connect(sqlite_db_path) as con:
        cur = con.cursor()

        cur.execute('''INSERT  INTO findmespot_keys (fms_key, last_rqs_ts, last_waypoint_ts) VALUES (?, ?, ?)''',
                    (str(fms_trip_id), date_start, date_end))
        db_id = cur.execute('''SELECT fms_key_id from findmespot_keys where fms_key = ?''',
                            (str(fms_trip_id),)).fetchall()[0][0]
        cur.execute('''INSERT INTO trips VALUES (?, ?, ?, ?)''',
                    (str(trip_name), date_start, date_end, int(db_id)))
        con.commit()
