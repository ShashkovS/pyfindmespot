#! /bin/python3

import requests
import json
from db_functions import *

# СОГЛАШЕНИЕ: Все timestamp'ы (datetime) только в UTC (GMT +00:00, а не GMT +03:00 и т.п.)

FIND_ME_SPOT_URL = r'https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/{key}/message.json?startDate={startDate}&endDate={endDate}'


def fetch_from_findmespot(key: str, start_ts=ZERO_TS):
    # key, finish_ts, last_rqs_t = get_trip_attributes(key)
    # finish_ts = db_ts_to_UTC_ts(finish_ts)
    # last_rqs_t = db_ts_to_UTC_ts(last_rqs_t)
    finish_ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10)
    # finish_ts = datetime.datetime.strptime(finish_ts, "%Y-%m-%dT%H:%M:%SZ")
    # if datetime.datetime.now(datetime.timezone.utc) > finish_ts:
    #     return
    # The date/time format should be 2009-01-22T13:08:55-0800
    # startDate=                     2019-03-13T09:48:26+0000
    # WTH!!! startDate in -08:00 timezone and enddate in UTC!
    url = FIND_ME_SPOT_URL.format(
        key=key,
        startDate=UTC_ts_to_fms_ts(finish_ts),
        endDate=now_time_utc().astimezone(datetime.timezone(offset=datetime.timedelta(hours=-8))).strftime("%Y-%m-%dT%H:%M:%S%z"),
        # endDate=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    )
    print(url)
    rq = requests.get(url)
    data_json = rq.content.decode('utf-8')
    data = json.loads(data_json)
    print(data_json)
    messages = data['response']['feedMessageResponse']['messages']['message']
    new_messages = [mess for mess in messages if fms_ts_to_UTC_ts(mess['dateTime']) > start_ts]
    if new_messages:
        write_waypoints_to_db(new_messages, key)


def main():
    check_base()
    # now_fms_keys_id = all_current_trips()
    now_fms_keys_id = [['0qHqjJzFKEQun9tMae2TZN8Dp1a4Di487']]
    for id in now_fms_keys_id:
        fetch_from_findmespot(id[0])


if __name__ == '__main__':
    main()
