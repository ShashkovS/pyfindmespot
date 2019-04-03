import datetime

ZERO_TS = datetime.datetime(2000, 1, 1, 0, 0).astimezone(datetime.timezone.utc)


def now_time_utc():
    return datetime.datetime.now().astimezone(datetime.timezone.utc)


def UTC_ts_to_fms_ts(dt):
    return dt.astimezone(datetime.timezone(offset=datetime.timedelta(hours=-8))).strftime("%Y-%m-%dT%H:%M:%S%z")


def fms_ts_to_UTC_ts(ts_utc):
    dt = datetime.datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%S%z")
    return dt.astimezone(datetime.timezone.utc)


def db_ts_to_UTC_ts(ts_utc):
    dt = datetime.datetime.strptime(ts_utc, "%Y-%m-%d %H:%M:%S%z")
    # dt = datetime.datetime.fromisoformat(ts_utc)
    return dt.astimezone(datetime.timezone.utc)


def UTC_ts_to_db_ts(ts_utc: datetime.datetime):
    return ts_utc.strftime("%Y-%m-%d %H:%M:%S%z")


def url_ts_to_UTC_ts(dt):
    return datetime.datetime.strptime(dt, "%d-%m-%YT%H:%M:%S%z")
