import pytz
from datetime import datetime, date


def user_local_date(user_tz: str) -> date:
    utc_tz = pytz.utc
    user_tz = pytz.timezone(user_tz)
    now_utc = utc_tz.localize(datetime.utcnow())
    date_now_user_tz = now_utc.astimezone(user_tz).date()

    return date_now_user_tz
