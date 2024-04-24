"""This example shows how to perform a tag analysis for all tag-based transactions for the last 6 weeks."""

# Import modules
import os
import sys
from pathlib import Path

# Append the base repo to the relative path, so that the local imports work as expected
BASE_REPO_PATH = Path(os.path.abspath(__file__)).parents[1].as_posix()
sys.path.append(BASE_REPO_PATH)

# Local imports
from src.helpers.up_toolkit import (  # noqa (import not at top)
    perform_budget_versus_spend_tag_analysis,
)
from src.shared.logging.logger import InternalLogger  # noqa (import not at top)
from src.shared.settings import DEFAULT_LOG_FILE, OUTPUT_DIR, TIMESTAMP, INPUT_DIR  # noqa (import not at top)
from src.transformers.time_transformers import calculate_n_weeks_ago_to_timestamp  # noqa (import not at top)

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="example_budget_tracker")


if __name__ == "__main__":
    timestamp_now = TIMESTAMP
    timestamp_for_filename = TIMESTAMP.replace(":", "-")
    # Retrieve the account that you want to perform the analysis on, in our example it's a 2Up Spending account
    account_name = "2Up Spending"
    # Generate a timestamp, so we can retrieve only the last six weeks of transactions
    six_weeks_ago_timestamp = calculate_n_weeks_ago_to_timestamp(timestamp_as_string=timestamp_now, weeks_ago=6)
    # Perform a budget vs spend analysis for the last six weeks and save to an Excel file.
    # Set your lower and upper variance limits across all tag budgets. This allows you to see what is over or under an
    # acceptance range, based on your criteria.
    lower_variance_limit: float = 95.00  # Anything 95% or lower of the budgeted range would be deemed a variance
    upper_variance_limit: float = 112.50  # Anything 112.5% or higher of the budgeted range would be deemed a variance
    perform_budget_versus_spend_tag_analysis(
        account_name=account_name,
        start_timestamp=six_weeks_ago_timestamp,
        end_timestamp=timestamp_now,
        input_budget_dir=INPUT_DIR,
        input_filename="budget-example.csv",
        output_dir=OUTPUT_DIR,
        output_filename=f"{timestamp_for_filename}-budget_vs_spend.xlsx",
        lower_variance_limit=lower_variance_limit,
        upper_variance_limit=upper_variance_limit,
    )
