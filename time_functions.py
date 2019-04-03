from datetime import datetime, timezone, timedelta
UTC = timezone.utc
ZERO_TS = datetime(2000, 1, 1, 0, 0, tzinfo=UTC)
TS_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

# Есть три формата даты:
# В базе храним '1999-12-31T21:00:00+0000'
# В url-запросе к findmespot.com нужно указать время в часом поясе -08:00
# А в ответ в треке придёт время в формате UTC

def now_time_utc() -> datetime:
    return datetime.now(tz=UTC)


def UTC_ts_to_FMS_URL_ts(dt) -> str:
    return dt.astimezone(timezone(offset=timedelta(hours=-8))).strftime(TS_FORMAT)


def str_ts_to_UTC_ts(ts_str: str) -> datetime:
    return datetime.strptime(ts_str, TS_FORMAT).astimezone(UTC)


def UTC_ts_to_str_ts(ts_utc: datetime) -> str:
    return ts_utc.strftime(TS_FORMAT)
