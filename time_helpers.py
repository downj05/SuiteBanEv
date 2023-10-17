from datetime import datetime as dt
import human_readable as hr


def ts_to_str(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def date_str_to_time_ago(date_str):
    # Takes in a date like '2023-10-09T11:12:32Z' and uses human_readable to convert it to a time ago string
    return hr.date_time(dt.now() - dt.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ"))
