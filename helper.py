import datetime
import pytz
from pytz import timezone
import os
from dotenv import load_dotenv
from datetime import datetime
import json

def get_time_in_timezone(req_time: datetime, target_timezone: str):
    return req_time.astimezone(timezone(target_timezone))

if __name__ == '__main__':
    load_dotenv()
    TIMEZONES = json.loads(os.getenv('TIMEZONES'))
    res = get_time_in_timezone(datetime.now(), TIMEZONES['ella'])
    print(res)