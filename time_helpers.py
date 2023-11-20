from datetime import datetime as dt
import datetime
import human_readable as hr
import re


def parse_duration(duration_str):
    if duration_str.lower() == "perm":
        return -1
    else:
        # Use regular expressions to extract numeric values and units
        matches = re.findall(r"(\d+)([sdhwmMy])", duration_str)
        seconds = 0

        for match in matches:
            value, unit = match
            value = int(value)
            if unit == "s":
                seconds += value
            elif unit == "m":
                seconds += value * 60
            elif unit == "h":
                seconds += value * 3600
            elif unit == "d":
                seconds += value * 86400
            elif unit == "w":
                seconds += value * 604800
            elif unit == "M":
                seconds += value * 2592000  # Assuming 30 days in a month
            elif unit == "y":
                seconds += value * 31536000  # Assuming 365 days in a year
            else:
                raise ValueError(f"Invalid unit: {unit}")

        return seconds


def ts_to_str(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def ts_to_str_ago(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return hr.date_time(dt.now() - dt.fromtimestamp(ts))


def format_time(seconds):
    if seconds < 0:
        return "Invalid input (negative seconds)"

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_parts = []
    if hours:
        time_parts.append(f"{hours}h")
    if minutes:
        time_parts.append(f"{minutes}m")
    if seconds or not (hours or minutes):
        time_parts.append(f"{seconds}s")

    return ''.join(time_parts)


def duration_to_str(duration: int):
    # is a length of time in seconds, if its -1 its permanent
    if duration == -1:
        return "permanent"
    else:
        return hr.time_delta(datetime.timedelta(seconds=duration))


def git_time_str_to_time_ago(date_str):
    # Takes in a date like '2023-10-09T11:12:32Z' and uses human_readable to convert it to a time ago string
    # git time seems to always be off by 12 hours, so we add 12 hours to the current time
    return hr.date_time(
        dt.now()
        - dt.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        - datetime.timedelta(hours=12)
    )
