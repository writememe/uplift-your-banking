"""This example contains multiple report workflows."""

# Import modules
import os
import sys
from pathlib import Path

# Append the base repo to the relative path, so that the local imports work as expected
BASE_REPO_PATH = Path(os.path.abspath(__file__)).parents[1].as_posix()
sys.path.append(BASE_REPO_PATH)


# Import modules

from src.helpers.up_toolkit import (  # noqa (import not at top)
    perform_all_tag_account_analysis,
    perform_budget_versus_spend_tag_analysis,
    retrieve_untagged_withdrawals,
    initialise_google_drive_client,
)
from src.shared.logging.logger import InternalLogger  # noqa (import not at top)
from src.shared.settings import (  # noqa (import not at top)
    DEFAULT_LOG_FILE,
    INPUT_DIR,
    OUTPUT_DIR,
    TIMESTAMP,
)
from src.transformers.time_transformers import (  # noqa (import not at top)
    calculate_n_months_ago_to_timestamp,
    calculate_n_weeks_ago_to_timestamp,
)
from src.exporters.outputs import upload_file_to_google_drive  # noqa (import not at top)

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="main_app")


def perform_last_week_transaction_analysis(
    start_timestamp: str,
    lower_variance_limit: float,
    upper_variance_limit: float,
    budget_input_filename: str,
    account_name: str,
) -> None:
    """Perform transaction analysis for the last week.

    Args:
        start_timestamp: The start timestamp range for which you want to perform the analysis.
        lower_variance_limit: The upper variance limit, which not reached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 97.50.
        upper_variance_limit: The upper variance limit, which when breached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 120.00.
        account_name:  The account name to perform the analysis on.
        budget_input_filename: The input CSV filename.

    Returns:
        N/A
    """
    one_week_ago_timestamp = calculate_n_weeks_ago_to_timestamp(timestamp_as_string=start_timestamp, weeks_ago=1)
    timestamp_for_filename = TIMESTAMP.replace(":", "-").replace(" ", "-")
    a = perform_budget_versus_spend_tag_analysis(
        account_name=account_name,
        start_timestamp=one_week_ago_timestamp,
        end_timestamp=start_timestamp,
        input_budget_dir=INPUT_DIR,
        input_filename=budget_input_filename,
        output_dir=OUTPUT_DIR,
        output_filename=f"{timestamp_for_filename}-last_week_budget_vs_spend.xlsx",
        lower_variance_limit=lower_variance_limit,
        upper_variance_limit=upper_variance_limit,
    )
    # Perform a tag analysis for all tag-based transactions for the last week and save to an Excel file
    b, _ = perform_all_tag_account_analysis(
        account_name=account_name,
        start_timestamp=one_week_ago_timestamp,
        end_timestamp=start_timestamp,
        output_filename=f"{timestamp_for_filename}-last_week_all_tag_based_analysis.xlsx",
    )
    # Retrieve the last week of withdrawals, which don't contain a tag and save to an Excel file
    c = retrieve_untagged_withdrawals(
        account_name=account_name,
        start_timestamp=one_week_ago_timestamp,
        end_timestamp=start_timestamp,
        output_dir=OUTPUT_DIR,
        output_filename=f"{timestamp_for_filename}-last_week_untagged-withdrawals.xlsx",
    )
    drive_client = initialise_google_drive_client()
    upload_file_to_google_drive(
        file_path=a, folder_id="1X7gsxRg7uHEaSc2PiUJz9pWO65ynwRbu", file_type="xlsx", drive_client=drive_client
    )  # noqa
    upload_file_to_google_drive(
        file_path=b, folder_id="1X7gsxRg7uHEaSc2PiUJz9pWO65ynwRbu", file_type="xlsx", drive_client=drive_client
    )  # noqa
    upload_file_to_google_drive(
        file_path=c, folder_id="1X7gsxRg7uHEaSc2PiUJz9pWO65ynwRbu", file_type="xlsx", drive_client=drive_client
    )  # noqa
    pass


def perform_last_four_weeks_transaction_analysis(
    start_timestamp: str,
    lower_variance_limit: float,
    upper_variance_limit: float,
    budget_input_filename: str,
    account_name: str,
) -> None:
    """Perform transaction analysis for the last 4 weeks.

    Args:
        start_timestamp: The start timestamp range for which you want to perform the analysis.
        lower_variance_limit: The upper variance limit, which not reached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 97.50.
        upper_variance_limit: The upper variance limit, which when breached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 120.00.
        account_name:  The account name to perform the analysis on.
        budget_input_filename: The input CSV filename.

    Returns:
        N/A
    """
    timestamp_for_filename = TIMESTAMP.replace(":", "-").replace(" ", "-")
    four_weeks_ago_timestamp = calculate_n_weeks_ago_to_timestamp(timestamp_as_string=start_timestamp, weeks_ago=4)
    perform_budget_versus_spend_tag_analysis(
        account_name=account_name,
        start_timestamp=four_weeks_ago_timestamp,
        end_timestamp=start_timestamp,
        input_budget_dir=INPUT_DIR,
        input_filename=budget_input_filename,
        output_dir=OUTPUT_DIR,
        output_filename=f"{timestamp_for_filename}-last_4_weeks_budget_vs_spend.xlsx",
        lower_variance_limit=lower_variance_limit,
        upper_variance_limit=upper_variance_limit,
    )
    # Perform a tag analysis for all tag-based transactions for the last 4 weeks and save to an Excel file
    perform_all_tag_account_analysis(
        account_name=account_name,
        start_timestamp=four_weeks_ago_timestamp,
        end_timestamp=start_timestamp,
        output_filename=f"{timestamp_for_filename}-last_4_weeks_all_tag_based_analysis.xlsx",
    )
    # Retrieve the last 4 weeks of withdrawals, which don't contain a tag and save to an Excel file
    retrieve_untagged_withdrawals(
        account_name=account_name,
        start_timestamp=four_weeks_ago_timestamp,
        end_timestamp=start_timestamp,
        output_dir=OUTPUT_DIR,
        output_filename=f"{timestamp_for_filename}-last_4_weeks_untagged-withdrawals.xlsx",
    )
    pass


def main() -> None:
    """Main workflow for the application."""
    timestamp_now = TIMESTAMP
    # Retrieve the account that you want to perform the analysis on, in our example it's a 2Up Spending account
    account_name = "2Up Spending"
    # Perform a budget vs spend analysis for the last six weeks and save to an Excel file.
    # Set your lower and upper variance limits across all tag budgets. This allows you to see what is over or under an
    # acceptance range, based on your criteria.
    lower_variance_limit: float = 95.00  # Anything 95% or lower of the budgeted range would be deemed a variance
    upper_variance_limit: float = 112.50  # Anything 112.5% or higher of the budgeted range would be deemed a variance
    budget_input_filename = "budget-example.csv"
    perform_last_week_transaction_analysis(
        start_timestamp=timestamp_now,
        lower_variance_limit=lower_variance_limit,
        upper_variance_limit=upper_variance_limit,
        budget_input_filename=budget_input_filename,
        account_name=account_name,
    )
    perform_last_four_weeks_transaction_analysis(
        start_timestamp=timestamp_now,
        lower_variance_limit=lower_variance_limit,
        upper_variance_limit=upper_variance_limit,
        budget_input_filename=budget_input_filename,
        account_name=account_name,
    )


if __name__ == "__main__":
    main()
