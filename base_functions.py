import sqlite3
import datetime


DB_DEFAULT_PATH = 'db/tracks.db'
NOW_TIME = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")


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


def call_fetch_from_fms(path, id):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key, last_waypoint_ts, last_rqs_ts FROM findmespot_keys WHERE fms_key_id = ?""", (id, ))
        key, start_t, last_rqs_t = c.fetchall()
        if datetime.datetime.strptime(last_rqs_t, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=3) <= datetime.datetime.now():
            fetch_from_findmespot(key, start_t)


def all_current_trips(path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""SELECT fms_key_id FROM trips WHERE date_e >= ?""", (NOW_TIME, ))
        return c.fetchall()


def updating_tables(messages: dict, key: str, path=DB_DEFAULT_PATH):
    with sqlite3.connect(path) as conn:
        try:
            conn.begin()
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
        except:
            conn.rollback()
