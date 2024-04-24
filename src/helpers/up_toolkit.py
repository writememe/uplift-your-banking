"""Up toolkit helpers."""

# Import modules
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from upbankapi import Client, NotAuthorizedException
from upbankapi.models import PaginatedList, Transaction
from upbankapi.models.accounts import Account

from src.exporters.outputs import output_dfs_to_excel
from src.ingestors.budget_ingestors import load_csv_budget_to_df
from src.shared.logging.logger import InternalLogger  # noqa
from src.shared.settings import DEFAULT_LOG_FILE, DEFAULT_TIMESTAMP_FORMAT, OUTPUT_DIR, TIMESTAMP
from src.transformers.data_transformers import (
    calculate_weekly_budget_variance,
    convert_transactions_to_df,
    filter_transactions_by_tag,
    filter_transactions_by_withdrawals_only,
    filter_transactions_with_empty_tag,
)
from src.transformers.time_transformers import calculate_time_periods_between_two_dates

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="up_helpers")


def initialise_up_bank_client(token: str = "") -> Client:  # nosec (hardcoded password)
    """Initialise the Up bank API client by utilising the ping endpoint to validate credentials.

    Args:
        token: The API access token (https://developer.up.com.au/#getting-started). Optionally this will read
        in the UP_TOKEN environmental variable when not supplied into this function.
            Defaults to "".

    Returns:
        up_bank_client: Initialised synchronous client for interacting with Up's API.
    """
    up_bank_client = Client(token=token) if token else Client()
    try:
        user_id = up_bank_client.ping()
        logger.info(f"Authorized: {user_id}")
        return up_bank_client
    except NotAuthorizedException as not_auth_err:
        logger.critical(f"The token is invalid. Error: {not_auth_err}. Please check your token and try again.")
        sys.exit(2)


def retrieve_specific_account(account_id: str, up_bank_client: Client) -> Account:
    """Retrieve a specific account from the Up Bank.

    Args:
        account_id: The account ID to be retrieved.
            Example: 2d8a6518-24ad-4506-9555-a78238c2ac2e
        up_bank_client: Initialised synchronous client for interacting with Up's API.

    Returns:
        up_bank_account: An Up Account, ready for future processing.
    """
    logger.info(f"Retrieving account ID: {account_id}")
    up_bank_account: Account = up_bank_client.account(account_id)
    logger.info(
        f"Account ID: {account_id} retrieved. Account Name: {up_bank_account.name} "
        f"- Ownership Type: {up_bank_account.ownership_type}"
    )
    return up_bank_account


def retrieve_transactions_from_account(
    up_bank_account: Account,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    transaction_limit: int = 0,
) -> PaginatedList[Transaction]:
    """Retrieve transactions from an elected account, taking optional parameters to limit the results.

    Args:
        up_bank_account: An Up Account, ready for processing.
        since: The start `datetime` from which to return records.
            Defaults to None.
        until: The end `datetime` up to which to return records.
            Defaults to None.
        transaction_limit: The amount of transactions to limit in the retrieval.
            Defaults to 0.

    Returns:
        all_transactions: A list of transactions, ready for future processing.
    """
    if transaction_limit:
        logger.info(f"Retrieving last {transaction_limit} transactions for {up_bank_account.name}")
    logger.info(f"Retrieving transactions for account name: {up_bank_account.name}")
    all_transactions = up_bank_account.transactions(limit=transaction_limit, since=since, until=until)
    logger.info(f"Retrieved transactions for account name: {up_bank_account.name}")
    return all_transactions


def filter_by_account_name(up_bank_client: Client, account_name: str) -> Account | None:
    """Filter all accounts for an account name, and return for future processing.

    Args:
        up_bank_client: Initialised synchronous client for interacting with Up's API.
        account_name: The account name to be retrieved.

    Returns:
        account: An Up Account, ready for processing.
    """
    accounts = up_bank_client.accounts()
    account_names: List[str] = []
    for account in accounts:
        account_names.append(account.name)
        if account.name == account_name:
            return account
    logger.error(
        f"Unable to find account name: {account_name} "
        f"in list of accounts: {account_names}."
        " Please check the account name and try again."
    )
    return None


def convert_datetime_to_string(date_object: datetime, timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT) -> str:
    """Convert a datetime object to a string.

    Args:
        date_object: The datetime object, to be converted to a string.
        timestamp_format: The timestamp format to be used in the string conversion.

    Returns:
        datetime_as_string: The datetime object in string format, as per the supplied timestamp_format.
    """
    datetime_as_string: str = ""
    # Return empty string for NaN values
    if pd.isnull(date_object):
        return datetime_as_string
    else:
        datetime_as_string = date_object.strftime(timestamp_format)
        return datetime_as_string


def perform_all_tag_account_analysis(
    account_name: str,
    start_timestamp: str,
    end_timestamp: str,
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = "all_tag_based_analysis.xlsx",
    generated_timestamp: str = TIMESTAMP,
) -> Tuple[str, pd.DataFrame]:
    """Perform an account-wide, tag-based analysis for the specified time period and save to an Excel file.

    This will perform a breakdown of spend on a per-tag basis, and generate a worksheet for each tag.

    Args:
        account_name:  The account name to perform the analysis on.
        start_timestamp: The start timestamp range for which you want to perform the analysis.
        end_timestamp: The end timestamp range for which you want to perform the analysis.
        timestamp_format: The timestamp format for the supplied start and end timestamps.
            Defaults to DEFAULT_TIMESTAMP_FORMAT.
        output_dir: The output directory to save the reports to.
            Defaults to OUTPUT_DIR.
        output_filename: The output filename to save the reports to.
            Defaults to "all_tag_based_analysis.xlsx".
        generated_timestamp: The timestamp which should be added for reporting purposes, so we know when the
        report was triggered.
            Defaults to TIMESTAMP.

    Returns:
        report_file: The Excel report file path which contains the results.
        all_tag_summary_df: The summary dataframe which contains the tag spend summary.
    """
    up_bank_client = initialise_up_bank_client()
    account_data = filter_by_account_name(up_bank_client=up_bank_client, account_name=account_name)
    if not account_data:
        logger.critical(
            f"Unable to retrieve account name: {account_name} and it's account_id attribute."
            " Please check that your account name is correct and try again."
        )
        sys.exit(2)
    else:
        account_id = account_data.id
    up_bank_account = retrieve_specific_account(account_id=account_id, up_bank_client=up_bank_client)
    start_time = datetime.strptime(start_timestamp, timestamp_format)
    end_time = datetime.strptime(end_timestamp, timestamp_format)
    time_difference_in_days, time_difference_in_weeks, time_difference_in_months = (
        calculate_time_periods_between_two_dates(start_time=start_time, end_time=end_time)
    )
    all_transactions = retrieve_transactions_from_account(
        up_bank_account=up_bank_account, since=start_time, until=end_time
    )
    all_transactions_df = convert_transactions_to_df(up_bank_transactions=all_transactions)
    all_tags = all_transactions_df["tags"].unique()
    all_tag_summary_data: List[Dict[str, Any]] = []
    tag_specific_df_results: Dict[str, pd.DataFrame] = {}
    for tag in all_tags:
        filtered_tag_df = filter_transactions_by_tag(df=all_transactions_df, tag=tag)
        filtered_tag_df.loc[:, ("settled_at")] = filtered_tag_df["settled_at"].apply(convert_datetime_to_string)
        filtered_tag_df.loc[:, ("created_at")] = filtered_tag_df["created_at"].apply(convert_datetime_to_string)
        tag_specific_df_results[tag] = filtered_tag_df
        total_tag_spend = filtered_tag_df["amount"].sum()
        total_tag_spend = abs(total_tag_spend)
        tag_weekly_spend = total_tag_spend / time_difference_in_weeks
        tag_monthly_spend = total_tag_spend / time_difference_in_months
        tag_summary_data: Dict[str, Any] = {
            "tag": tag,
            "total_spend": total_tag_spend,
            "weekly_spend": tag_weekly_spend,
            "monthly_spend": tag_monthly_spend,
        }
        logger.info(f"Tag analysis data: {tag_summary_data}")
        all_tag_summary_data.append(tag_summary_data)
    report_summary_dict: Dict[str, Any] = {
        "from_timestamp": [start_timestamp],
        "to_timestamp": [end_timestamp],
        "generated_at": [generated_timestamp],
        "total_days": [time_difference_in_days],
        "total_weeks": [time_difference_in_weeks],
        "total_months": [time_difference_in_months],
    }
    report_summary_df = pd.DataFrame(report_summary_dict)
    all_tag_summary_df = pd.DataFrame(all_tag_summary_data)
    all_tag_summary_df = all_tag_summary_df.sort_values(by=["total_spend"], ascending=False)
    final_tag_df_results: Dict[str, pd.DataFrame] = {
        "report_summary": report_summary_df,
        "tag_summary": all_tag_summary_df,
    }
    for df_name, df in tag_specific_df_results.items():
        final_tag_df_results[df_name] = df
    report_file = output_dfs_to_excel(df_list=final_tag_df_results, output_dir=output_dir, filename=output_filename)
    return report_file, all_tag_summary_df


def perform_tag_account_analysis(
    account_name: str,
    start_timestamp: str,
    end_timestamp: str,
    tags_to_be_analysed: List[str],
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = "tag_based_analysis.xlsx",
    generated_timestamp: str = TIMESTAMP,
) -> Tuple[str, pd.DataFrame]:
    """Perform an account-wide, on the supplied tags for the specified time period and save to an Excel file.

    Args:
        account_name:  The account name to perform the analysis on.
        start_timestamp: The start timestamp range for which you want to perform the analysis.
        end_timestamp: The end timestamp range for which you want to perform the analysis.
        tags_to_be_analysed: A list of tags to perform the analysis on.
        timestamp_format: The timestamp format for the supplied start and end timestamps.
            Defaults to DEFAULT_TIMESTAMP_FORMAT.
        output_dir: The output directory to save the reports to.
            Defaults to OUTPUT_DIR.
        output_filename: The output filename to save the reports to.
            Defaults to "tag_based_analysis.xlsx".
        generated_timestamp: The timestamp which should be added for reporting purposes, so we know when the
        report was triggered.
            Defaults to TIMESTAMP.


    Returns:
        report_file: The Excel report file path which contains the results.
        all_tag_summary_df: The summary dataframe which contains the tag spend summary.
    """
    up_bank_client = initialise_up_bank_client()
    account_data = filter_by_account_name(up_bank_client=up_bank_client, account_name=account_name)
    if not account_data:
        logger.critical(
            f"Unable to retrieve account name: {account_name} and it's account_id attribute."
            " Please check that your account name is correct and try again."
        )
        sys.exit(2)
    else:
        account_id = account_data.id
    up_bank_account = retrieve_specific_account(account_id=account_id, up_bank_client=up_bank_client)
    start_time = datetime.strptime(start_timestamp, timestamp_format)
    end_time = datetime.strptime(end_timestamp, timestamp_format)
    time_difference_in_days, time_difference_in_weeks, time_difference_in_months = (
        calculate_time_periods_between_two_dates(start_time=start_time, end_time=end_time)
    )
    all_transactions = retrieve_transactions_from_account(
        up_bank_account=up_bank_account, since=start_time, until=end_time
    )
    all_transactions_df = convert_transactions_to_df(up_bank_transactions=all_transactions)
    all_tag_summary_data: List[Dict[str, Any]] = []
    tag_specific_df_results: Dict[str, pd.DataFrame] = {}
    for tag in tags_to_be_analysed:
        filtered_tag_df = filter_transactions_by_tag(df=all_transactions_df, tag=tag)
        filtered_tag_df.loc[:, ("settled_at")] = filtered_tag_df["settled_at"].apply(convert_datetime_to_string)
        filtered_tag_df.loc[:, ("created_at")] = filtered_tag_df["created_at"].apply(convert_datetime_to_string)
        tag_specific_df_results[tag] = filtered_tag_df
        total_tag_spend = filtered_tag_df["amount"].sum()
        total_tag_spend = abs(total_tag_spend)
        tag_weekly_spend = total_tag_spend / time_difference_in_weeks
        tag_monthly_spend = total_tag_spend / time_difference_in_months
        tag_summary_data: Dict[str, Any] = {
            "tag": tag,
            "total_spend": total_tag_spend,
            "weekly_spend": tag_weekly_spend,
            "monthly_spend": tag_monthly_spend,
        }
        logger.info(f"Tag analysis data: {tag_summary_data}")
        all_tag_summary_data.append(tag_summary_data)
    report_summary_dict: Dict[str, Any] = {
        "from_timestamp": [start_timestamp],
        "to_timestamp": [end_timestamp],
        "generated_at": [generated_timestamp],
        "total_days": [time_difference_in_days],
        "total_weeks": [time_difference_in_weeks],
        "total_months": [time_difference_in_months],
    }
    report_summary_df = pd.DataFrame.from_dict(report_summary_dict)
    all_tag_summary_df = pd.DataFrame(all_tag_summary_data)
    all_tag_summary_df = all_tag_summary_df.sort_values(by=["total_spend"], ascending=False)
    final_tag_df_results: Dict[str, pd.DataFrame] = {
        "report_summary": report_summary_df,
        "tag_summary": all_tag_summary_df,
    }
    for df_name, df in tag_specific_df_results.items():
        final_tag_df_results[df_name] = df
    report_file = output_dfs_to_excel(df_list=final_tag_df_results, output_dir=output_dir, filename=output_filename)
    return report_file, all_tag_summary_df


def perform_budget_versus_spend_tag_analysis(
    account_name: str,
    start_timestamp: str,
    end_timestamp: str,
    input_budget_dir: str,
    input_filename: str,
    output_dir: str = OUTPUT_DIR,
    output_filename: str = "budget_vs_spend.xlsx",
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
    generated_timestamp: str = TIMESTAMP,
    upper_variance_limit: float = 120.00,
    lower_variance_limit: float = 97.50,
) -> str:  # noqa
    """Perform an account-wide analysis of your tag-based budget versus your spend for the specified time period.

    Args:
        account_name:  The account name to perform the analysis on.
        start_timestamp: The start timestamp range for which you want to perform the analysis.
        end_timestamp: The end timestamp range for which you want to perform the analysis.
        input_budget_dir: The input directory which contains budget file.
        input_filename: The input CSV filename.
        output_dir: The output directory to save the reports to.
            Defaults to OUTPUT_DIR.
        output_filename: The output filename to save the reports to.
            Defaults to "budget_vs_spend.xlsx".
        timestamp_format: The timestamp format for the supplied start and end timestamps.
            Defaults to DEFAULT_TIMESTAMP_FORMAT.
        generated_timestamp: The timestamp which should be added for reporting purposes, so we know when the
        report was triggered.
            Defaults to TIMESTAMP.
        upper_variance_limit: The upper variance limit, which when breached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 120.00.
        lower_variance_limit: The upper variance limit, which not reached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 97.50.

    Returns:
        report_file: The Excel report file path which contains the results.
    """
    _, all_tag_summary_df = perform_all_tag_account_analysis(
        account_name=account_name, end_timestamp=end_timestamp, start_timestamp=start_timestamp
    )
    budget_df = load_csv_budget_to_df(input_dir=input_budget_dir, input_filename=input_filename)
    budget_spend_merged_df = pd.merge(left=all_tag_summary_df, right=budget_df, on="tag", how="left")
    budget_spend_df = calculate_weekly_budget_variance(
        df=budget_spend_merged_df, upper_variance_limit=upper_variance_limit, lower_variance_limit=lower_variance_limit
    )
    # NOTE: Dropping the 'monthly_spend' column as the current budget tracker is based on a 'weekly_budget" amount.
    # If you  wanted to adjust your budgeting to monthly, you could define your own "monthly_budget" key and
    # write your own calculate_monthly_budget_variance function
    budget_columns = budget_spend_df.columns.to_list()
    for column in budget_columns:
        logger.critical(f"Column Name: {column}")
    logger.critical(f"Columns: {budget_spend_df.columns.to_list()}")

    if "weekly_budget_variance" in budget_spend_df.columns.to_list():
        budget_spend_merged_df = budget_spend_df.drop(columns=["monthly_spend"])
    start_time = datetime.strptime(start_timestamp, timestamp_format)
    end_time = datetime.strptime(end_timestamp, timestamp_format)
    time_difference_in_days, time_difference_in_weeks, time_difference_in_months = (
        calculate_time_periods_between_two_dates(start_time=start_time, end_time=end_time)
    )
    report_summary_dict: Dict[str, Any] = {
        "from_timestamp": [start_timestamp],
        "to_timestamp": [end_timestamp],
        "generated_at": [generated_timestamp],
        "total_days": [time_difference_in_days],
        "total_weeks": [time_difference_in_weeks],
        "total_months": [time_difference_in_months],
    }
    report_summary_df = pd.DataFrame.from_dict(report_summary_dict)
    df_list: Dict[str, pd.DataFrame] = {
        "report_summary": report_summary_df,
        "budget_vs_spend": budget_spend_df,
    }
    report_file = output_dfs_to_excel(df_list=df_list, output_dir=output_dir, filename=output_filename)
    return report_file


def retrieve_untagged_withdrawals(
    account_name: str,
    start_timestamp: str,
    end_timestamp: str,
    output_dir: str,
    output_filename: str = OUTPUT_DIR,
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
    generated_timestamp: str = TIMESTAMP,
) -> str:
    """Retrieve the untagged transactions for an account for a specified time period and save to an Excel file.

    Args:
        account_name:  The account name to perform the analysis on.
        start_timestamp: The start timestamp range for which you want to perform the analysis.
        end_timestamp: The end timestamp range for which you want to perform the analysis.
        output_dir: The output directory to save the reports to.
            Defaults to OUTPUT_DIR.
        output_filename: The output filename to save the reports to.
            Defaults to "tag_based_analysis.xlsx".
        timestamp_format: The timestamp format for the supplied start and end timestamps.
            Defaults to DEFAULT_TIMESTAMP_FORMAT.
        generated_timestamp: The timestamp which should be added for reporting purposes, so we know when the
        report was triggered.
            Defaults to TIMESTAMP.

    Returns:
        report_file: The Excel report file path which contains the results.
    """
    up_bank_client = initialise_up_bank_client()
    account_data = filter_by_account_name(up_bank_client=up_bank_client, account_name=account_name)
    if not account_data:
        logger.critical(
            f"Unable to retrieve account name: {account_name} and it's account_id attribute."
            " Please check that your account name is correct and try again."
        )
        sys.exit(2)
    else:
        account_id = account_data.id
    up_bank_account = retrieve_specific_account(account_id=account_id, up_bank_client=up_bank_client)
    start_time = datetime.strptime(start_timestamp, timestamp_format)
    end_time = datetime.strptime(end_timestamp, timestamp_format)
    time_difference_in_days, time_difference_in_weeks, time_difference_in_months = (
        calculate_time_periods_between_two_dates(start_time=start_time, end_time=end_time)
    )
    all_transactions = retrieve_transactions_from_account(
        up_bank_account=up_bank_account, since=start_time, until=end_time
    )
    all_transactions_df = convert_transactions_to_df(up_bank_transactions=all_transactions)
    withdrawals_df = filter_transactions_by_withdrawals_only(df=all_transactions_df)
    untagged_withdrawals_df = filter_transactions_with_empty_tag(df=withdrawals_df)
    untagged_withdrawals_df.loc[:, ("settled_at")] = untagged_withdrawals_df["settled_at"].apply(
        convert_datetime_to_string
    )
    untagged_withdrawals_df.loc[:, ("created_at")] = untagged_withdrawals_df["created_at"].apply(
        convert_datetime_to_string
    )
    report_summary_dict: Dict[str, Any] = {
        "from_timestamp": [start_timestamp],
        "to_timestamp": [end_timestamp],
        "generated_at": [generated_timestamp],
        "total_days": [time_difference_in_days],
        "total_weeks": [time_difference_in_weeks],
        "total_months": [time_difference_in_months],
    }
    report_summary_df = pd.DataFrame.from_dict(report_summary_dict)
    df_list: Dict[str, pd.DataFrame] = {
        "report_summary": report_summary_df,
        "untagged_withdrawals": untagged_withdrawals_df,
    }
    report_file = output_dfs_to_excel(df_list=df_list, output_dir=output_dir, filename=output_filename)
    return report_file
