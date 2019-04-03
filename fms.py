#! /bin/python3

import requests
import json
from db_functions import *

# СОГЛАШЕНИЕ: Все timestamp'ы (datetime) только в UTC (GMT +00:00, а не GMT +03:00 и т.п.)

FIND_ME_SPOT_URL = r'https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/{key}/message.json?startDate={startDate}&endDate={endDate}'


def fetch_from_findmespot(key: int):
    key, last_point_ts, last_rqs_t = get_trip_attributes(key)
    if now_time_utc() - last_rqs_t < timedelta(minutes=5):
        return
    url = FIND_ME_SPOT_URL.format(
        key=key,
        startDate=UTC_ts_to_FMS_URL_ts(last_point_ts + timedelta(seconds=1)),
        endDate=UTC_ts_to_FMS_URL_ts(now_time_utc()),
    )
    print(url)
    rq = requests.get(url)
    data_json = rq.content.decode('utf-8')
    data = json.loads(data_json)
    print(data_json)
    if 'errors' in data['response']:
        print(data['response'])
        messages = []
    else:
        messages = data['response']['feedMessageResponse']['messages']['message']
    write_waypoints_to_db(messages, key)


def main():
    check_base()
    now_fms_keys_id = all_current_trips()
    # now_fms_keys_id = [['0qHqjJzFKEQun9tMae2TZN8Dp1a4Di487']]
    print(now_fms_keys_id)
    for id in now_fms_keys_id:
        fetch_from_findmespot(id[0])


if __name__ == '__main__':
    main()
