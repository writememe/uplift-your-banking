"""This example shows how to retrieve all untagged withdrawals from a given account in the last three months."""

# Import modules
import os
import sys
from pathlib import Path

# Append the base repo to the relative path, so that the local imports work as expected
BASE_REPO_PATH = Path(os.path.abspath(__file__)).parents[1].as_posix()
sys.path.append(BASE_REPO_PATH)

# Local imports
from src.helpers.up_toolkit import (  # noqa (import not at top)
    retrieve_untagged_withdrawals,
)
from src.shared.logging.logger import InternalLogger  # noqa (import not at top)
from src.shared.settings import DEFAULT_LOG_FILE, OUTPUT_DIR, TIMESTAMP  # noqa (import not at top)
from src.transformers.time_transformers import calculate_n_months_ago_to_timestamp  # noqa (import not at top)

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="example_untagged_transactions")


if __name__ == "__main__":
    timestamp_now = TIMESTAMP
    timestamp_for_filename = TIMESTAMP.replace(":", "-")
    # Retrieve the account that you want to perform the analysis on, in our example it's a 2Up Spending account
    account_name = "2Up Spending"
    # Generate a timestamp, so we can retrieve only the last three months of transactions
    three_months_ago_timestamp = calculate_n_months_ago_to_timestamp(timestamp_as_string=timestamp_now, months_ago=3)
    # Retrieve the last three months of withdrawals, which don't contain a tag and save to an Excel file
    retrieve_untagged_withdrawals(
        account_name=account_name,
        start_timestamp=three_months_ago_timestamp,
        end_timestamp=timestamp_now,
        output_dir=OUTPUT_DIR,
        output_filename=f"{timestamp_for_filename}-untagged-withdrawals.xlsx",
    )
