"""Central settings file."""

import os
from datetime import datetime
from pathlib import Path

import pytz

# Get path of the current dir under which the file is executed.
dirname = os.path.dirname(__file__)

# Retrieve the repos src directory object, convert to string and assign to a variable for further usage
SRC_DIR_PATH = Path(os.path.abspath(__file__)).parents[1].as_posix()

# Retrieve the repos base directory object, convert to string and assign to a variable for further usage
BASE_REPO_PATH = Path(os.path.abspath(__file__)).parents[2].as_posix()

TTP_TEMPLATE_BASE_DIRECTORY = os.path.join(SRC_DIR_PATH, "templates", "ttp")
J2_TEMPLATE_BASE_DIRECTORY = os.path.join(SRC_DIR_PATH, "templates", "jinja2")
OUTPUT_DIR = os.path.join(
    BASE_REPO_PATH,
    "outputs",
)
LOG_DIR = os.path.join(BASE_REPO_PATH, "logs")
INPUT_DIR = os.path.join(BASE_REPO_PATH, "inputs")
Path(OUTPUT_DIR).mkdir(exist_ok=True, parents=True)
Path(LOG_DIR).mkdir(exist_ok=True, parents=True)
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "up_bank_toolkit.log")


# Time and timezone settings
DEFAULT_TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S"
_DEFAULT_TZ_NAME = "Australia/Sydney"
_TIMEZONE_AWARE_TIMESTAMP: datetime = datetime.now(tz=pytz.timezone(_DEFAULT_TZ_NAME))
TIMESTAMP: str = _TIMEZONE_AWARE_TIMESTAMP.strftime(DEFAULT_TIMESTAMP_FORMAT)
