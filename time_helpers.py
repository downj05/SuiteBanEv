from datetime import datetime as dt
import datetime
import human_readable as hr


def ts_to_str(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def ts_to_str_ago(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return hr.date_time(dt.now() - dt.fromtimestamp(ts))


def git_time_str_to_time_ago(date_str):
    # Takes in a date like '2023-10-09T11:12:32Z' and uses human_readable to convert it to a time ago string
    # git time seems to always be off by 12 hours, so we add 12 hours to the current time
    return hr.date_time(
        dt.now()
        - dt.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        - datetime.timedelta(hours=12)
    )
