import requests
import json
import pyperclip
import pprint
import os
from base_functions import *


ZERO_TS = datetime.datetime(2000, 1, 1, 0, 0)
FIND_ME_SPOT_URL = r'https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/{key}/message.json?startDate={startDate}'


def ts_to_UTC_str(ts):
    return (ts + datetime.timedelta(hours=-3)).isoformat(sep='T', timespec='seconds') + '-0000'


def fetch_from_findmespot(key: str, start_ts=ZERO_TS):
    path = sqlite_db_path
    url = FIND_ME_SPOT_URL.format(key=key, startDate=ts_to_UTC_str(ZERO_TS))
    rq = requests.get(url)
    data_json = rq.content.decode('utf-8')
    data = json.loads(data_json)
    pyperclip.copy(pprint.pformat(data))
    messages = data['response']['feedMessageResponse']['messages']['message']
    for mess in messages:
        if messages[mess]['dateTime'] > start_ts:  # Ещё будет функция перевода времени.
            update_tables(messages[mess], key)
        else:
            break


def main():
    check_base()
    now_fms_keys_id = all_current_trips()
    for id in now_fms_keys_id:
        call_fetch_from_fms(id[0])


if __name__ == '__main__':
    main()
