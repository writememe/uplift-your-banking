"""Time transformers."""

from datetime import datetime, timedelta
from typing import Tuple

from dateutil.relativedelta import relativedelta

from src.shared.logging.logger import InternalLogger  # noqa
from src.shared.settings import DEFAULT_LOG_FILE

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="time_transformers")


def calculate_n_hours_ago_to_timestamp(timestamp_as_string: str, hours_ago: int = 1) -> str:
    """Take a timestamp string, and return a timestamp string of n hours ago, whereby n is the number of hours.

    Args:
        timestamp_as_string: A timestamp string adhering to the string format of %Y-%m-%d %H:%M:%S
            Example: 2023-06-08 08:58:07
        hours_ago: The number of hours ago for which you would like the timestamp for.
            Defaults to 1.

    Returns:
        timestamp: Timestamp in the format 'YYYY-MM-DD HH:MM:SS'.
            Example based on above:
                2023-06-08 07:58:07
    """
    timestamp_as_datetime_object = datetime.strptime(timestamp_as_string, "%Y-%m-%d %H:%M:%S")
    n_hours_ago = timestamp_as_datetime_object + relativedelta(hours=-hours_ago)
    timestamp = n_hours_ago.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def calculate_n_days_ago_to_timestamp(timestamp_as_string: str, days_ago: int = 1) -> str:
    """Take a timestamp string, and return a timestamp string of n days ago, whereby n is the number of days.

    Args:
        timestamp_as_string: A timestamp string adhering to the string format of %Y-%m-%d %H:%M:%S
            Example: 2023-06-08 08:58:07
        days_ago: The number of days ago for which you would like the timestamp for.
            Defaults to 1.

    Returns:
        timestamp: Timestamp in the format 'YYYY-MM-DD HH:MM:SS'.
            Example based on above:
                2023-06-07 08:58:07
    """
    timestamp_as_datetime_object = datetime.strptime(timestamp_as_string, "%Y-%m-%d %H:%M:%S")
    n_days_ago = timestamp_as_datetime_object + relativedelta(days=-days_ago)
    timestamp = n_days_ago.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def calculate_n_weeks_ago_to_timestamp(timestamp_as_string: str, weeks_ago: int = 1) -> str:
    """Take a timestamp string, and return a timestamp string of n weeks ago, whereby n is the number of weeks.

    Args:
        timestamp_as_string: A timestamp string adhering to the string format of %Y-%m-%d %H:%M:%S
            Example: 2023-06-08 08:58:07
        weeks_ago: The number of weeks ago for which you would like the timestamp for.
            Defaults to 1.

    Returns:
        timestamp: Timestamp in the format 'YYYY-MM-DD HH:MM:SS'.
            Example based on above:
                2023-06-01 08:58:07
    """
    timestamp_as_datetime_object = datetime.strptime(timestamp_as_string, "%Y-%m-%d %H:%M:%S")
    n_weeks_ago = timestamp_as_datetime_object + relativedelta(weeks=-weeks_ago)
    timestamp = n_weeks_ago.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def calculate_n_months_ago_to_timestamp(timestamp_as_string: str, months_ago: int = 1) -> str:
    """Take a timestamp string, and return a timestamp string of n months ago, whereby n is the number of months.

    Args:
        timestamp_as_string: A timestamp string adhering to the string format of %Y-%m-%d %H:%M:%S
            Example: 2023-06-08 08:58:07
        months_ago: The number of months ago for which you would like the timestamp for.
            Defaults to 1.

    Returns:
        timestamp: Timestamp in the format 'YYYY-MM-DD HH:MM:SS'.
            Example based on above:
                2023-05-08 08:58:07
    """
    timestamp_as_datetime_object = datetime.strptime(timestamp_as_string, "%Y-%m-%d %H:%M:%S")
    n_months_ago = timestamp_as_datetime_object + relativedelta(months=-months_ago)
    timestamp = n_months_ago.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def calculate_time_periods_between_two_dates(start_time: datetime, end_time: datetime) -> Tuple[float, float, float]:
    """Calculate the various time periods between two dates, and return for further processing.

    Args:
        start_time: The start time of the two periods we want to calculate the difference on.
        end_time: The end time of the two periods we want to calculate the difference on.

    Returns:
        time_difference_in_days: The exact time difference in days.
        time_difference_in_weeks: The exact time difference in weeks.
        time_difference_in_months: The exact time difference in months.
    """
    time_difference = end_time - start_time
    time_difference_in_minutes = time_difference / timedelta(minutes=1)
    time_difference_in_days = time_difference / timedelta(days=1)
    time_difference_in_weeks = time_difference / timedelta(weeks=1)
    time_difference_in_months = calculate_days_to_months(days=time_difference_in_days)
    logger.debug(f"Start Time: {start_time} - End Time: {end_time} differences are as follows:")
    logger.debug(f"Time difference in minutes: {time_difference_in_minutes}")
    logger.debug(f"Time difference in days: {time_difference_in_days}")
    logger.debug(f"Time difference in weeks: {time_difference_in_weeks}")
    logger.debug(f"Time difference in months: {time_difference_in_months}")
    return time_difference_in_days, time_difference_in_weeks, time_difference_in_months


def calculate_days_to_months(days: float) -> float:
    """Convert the days into a months' equivalent value.

    Args:
        days: The exact days in float representation.

    Returns:
        months: The exact months in float representation.
    """
    average_days_in_month: float = 365 / 12
    months = days / average_days_in_month
    return months
