from fms import *
from db_functions import _create_base


def _create_dummy_data(path=sqlite_db_path):
    import random
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        for fms_key_id in range(2, 5):
            c.execute(
                f"""insert into findmespot_keys values ({fms_key_id}, 'asdfsjlibdummy{fms_key_id}', '0001-01-01T00:00:00Z', '0001-01-01T00:00:00Z')""")
            c.execute(
                f"""insert into trips values ('trip{fms_key_id}', '2018-04-0{fms_key_id}T00:00:00Z', '2018-06-0{fms_key_id}T00:00:00Z', {fms_key_id}) """)
            for point_num in range(random.randint(0, 100)):
                id_from_fms = f'{fms_key_id:04}_{point_num:04}'
                lat = random.random() * 90
                long = random.random() * 90
                ts = datetime.datetime(2018, 4, 1, 0, 0, 0) + datetime.timedelta(hours=point_num) + datetime.timedelta(
                    days=fms_key_id)
                batteryState = 'GOOD'
                msg = 'Bce cynep!'
                c.execute(f"""insert into waypoints (fms_key_id, id_from_fms, lat, long, alt, ts, batteryState, msg) 
                              values (?, ?, ?, ?, ?, ?, ?, ?) """,
                          (fms_key_id, id_from_fms, lat, long, 500, ts, batteryState, msg))
        fms_key_id = 1
        c.execute(
            f"""insert into findmespot_keys values ({fms_key_id}, '0N0t9EXiJA8115ifa6qTkfqNGgxoCpvla', '0001-01-01T00:00:00Z', '0001-01-01T00:00:00Z')""")
        c.execute(
            f"""insert into trips values ('real_track', '2018-04-0{fms_key_id}T00:00:00Z', '2018-06-0{fms_key_id}T00:00:00Z', {fms_key_id}) """)
        with open('db/test_track.txt') as f:
            data = f.readlines()
            for point_num, row in enumerate(data):
                id_from_fms = f'{fms_key_id:04}_{point_num:04}'
                lat, long, alt, ts = row.split()
                batteryState = 'GOOD'
                msg = 'Bce cynep!'
                c.execute(f"""insert into waypoints (fms_key_id, id_from_fms, lat, long, alt, ts, batteryState, msg) 
                              values (?, ?, ?, ?, ?, ?, ?, ?) """,
                          (fms_key_id, id_from_fms, lat, long, 500, ts, batteryState, msg))
        conn.commit()

        ar2 = c.execute("""select * from waypoints""").fetchall()


if __name__ == '__main__':
    _create_base()
    _create_dummy_data()
