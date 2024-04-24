from src.shared.logging.logger import InternalLogger  # noqa
from upbankapi.models import PaginatedList, Transaction
import pandas as pd
from typing import Any, Dict, List, Tuple
from src.shared.settings import DEFAULT_LOG_FILE
from math import isnan


# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="data_transformers")


def extract_transaction_category_data(transaction: Transaction) -> Tuple[str, str]:
    """Extract the transactions' category data, so that it can be normalised and stored in a dataframe.

    Args:
        transaction: An Up Transaction, ready to be processed.

    Returns:
        transaction_category_data: The transactions' category which is stored an as attribute on the Transaction object.
        transaction_parent_category_data: The transactions' parent category which is stored an as attribute on the
        Transaction object.
    """
    # Set defaults to empty string, so that we cannot extract the values, an empty value is returned.
    transaction_category_data: str = ""
    transaction_parent_category_data: str = ""
    # Try/except block to extract category ID.
    # NOTE: There are valid transactions which don't contain a category ID, such as deposits from other banking
    # institutions. We catch that exception, tune it down to a debug message and this is considered normal behaviour.
    try:
        transaction_category_data = transaction.category.id
    except AttributeError as attr_e:
        if transaction.amount > 0:
            logger.debug(
                f"Transaction category not found for transaction description: {transaction.description}, "
                f"setting to: '{transaction_category_data}'. Error: {attr_e}"
            )
        else:
            logger.warning(
                f"Transaction category not found for transaction description: {transaction.description}, "
                f"setting to: '{transaction_category_data}'. Error: {attr_e}"
            )
    # Try/except block to extract category parent ID.
    # NOTE: There are valid transactions which don't contain a category parent ID, such as deposits from other banking
    # institutions. We catch that exception, tune it down to a debug message and this is considered normal behaviour.
    try:
        logger.debug(f"Raw Data: {transaction.category.parent.id}")
        transaction_parent_category_data = transaction.category.parent.id
    except AttributeError as attr_e:
        if transaction.amount > 0:
            logger.debug(
                f"Transaction category not found for transaction description: {transaction.description}, "
                f"setting to: '{transaction_category_data}'. Error: {attr_e}"
            )
        else:
            logger.warning(
                f"Transaction parent category not found for transaction description: {transaction.description},"
                f" setting to: '{transaction_parent_category_data}'. Error: {attr_e}"
            )
    return transaction_category_data, transaction_parent_category_data


def extract_transaction_tag_data(transaction: Transaction) -> str:
    """Extract a transactions' tag data into a string of comma-seperated tags for further processing.

    Args:
        transaction: An Up Transaction, ready to be processed.

    Returns:
        transaction_tag_data: String representation of tags for further processing.
    """
    transaction_tag_data: str = ""
    # Try to extract the tags attribute off the transaction
    try:
        transaction_tag_list_data = transaction.tags
        logger.debug(f"Raw Data: {transaction_tag_list_data}")
        # Unpack the list of tag IDs and join them together back into a large,single string seperated by commas
        if transaction_tag_list_data:
            transaction_tag_names: List[str] = []
            for transaction_tag in transaction_tag_list_data:
                transaction_tag_names.append(transaction_tag.id)
            transaction_tag_data = ",".join(transaction_tag_names)
            return transaction_tag_data
    # NOTE: Not all transactions have a tag, so catch this exception and conditionally log a message
    except AttributeError as attr_e:
        # If it's a positive transaction (a deposit, log a debug message)
        if transaction.amount > 0:
            logger.debug(f"Transaction tags not found, setting to: '{transaction_tag_data}'. Error: {attr_e}")
        # Else, it's a negative transaction (a transaction, log a warning message)
        else:
            logger.warning(f"Transaction tags not found, setting to: '{transaction_tag_data}'. Error: {attr_e}")
    return transaction_tag_data


def extract_transaction_card_purchase_method(transaction: Transaction) -> Tuple[str, str]:
    """Extract a transactions' card purchase method and suffix data for further processing.

    Args:
        transaction: An Up Transaction, ready to be processed.

    Returns:
        transaction_card_purchase_method_data: The card purchase method for further processing.
        transaction_card_purchase_suffix_data: The card purchase suffix data for further processing.
    """
    transaction_card_purchase_method_data: str = ""
    transaction_card_purchase_suffix_data: str = ""
    # Try to extract the card purchase method attribute off the transaction
    try:
        transaction_card_purchase_method_data = transaction.card_purchase_method.method
    # NOTE: Not all transactions have a card purchase method, so catch this exception and conditionally log a message
    except AttributeError as attr_e:
        #  If it's a positive transaction (a deposit, log a debug message)
        if transaction.amount > 0:
            logger.debug(
                "Transaction card purchase method not found, setting to: "
                f"'{transaction_card_purchase_method_data}'. Error: {attr_e}"
            )
        # Else, it's a negative transaction (a transaction, log a warning message)
        else:
            logger.warning(
                "Transaction card purchase method not found, setting to: "
                f"'{transaction_card_purchase_method_data}'. Error: {attr_e}"
            )
    # NOTE: Not all transactions have a card purchase suffix, so catch this exception and conditionally log a message
    # Try to extract the card purchase suffix method attribute off the transaction
    try:
        transaction_card_purchase_suffix_data = transaction.card_purchase_method.card_suffix
    except AttributeError as attr_e:
        #  If it's a positive transaction (a deposit, log a debug message)
        if transaction.amount > 0:
            logger.debug(
                "Transaction card purchase card suffix not found, setting to: "
                f"'{transaction_card_purchase_suffix_data}'. Error: {attr_e}"
            )
        # Else, it's a negative transaction (a transaction, log a warning message)
        else:
            logger.warning(
                "Transaction card purchase card suffix not found, setting to: "
                f"'{transaction_card_purchase_suffix_data}'. Error: {attr_e}"
            )
    return transaction_card_purchase_method_data, transaction_card_purchase_suffix_data


def convert_transactions_to_df(up_bank_transactions: PaginatedList[Transaction]) -> pd.DataFrame:
    """Convert a list of Up Bank transactions into a Pandas dataframe.

    Args:
        up_bank_transactions: A list of Up Bank Transactions, ready for future processing.

    Returns:
        all_transactions_df: Pandas dataframe, containing normalised data about each transaction.
    """
    all_transactions: List[Dict[str, Any]] = []
    for transaction in up_bank_transactions:
        # Extract and normalise the values from the various elements of a transaction which have nested data.
        transaction_category_data, transaction_parent_category_data = extract_transaction_category_data(
            transaction=transaction
        )
        transaction_tag_data = extract_transaction_tag_data(transaction=transaction)
        transaction_card_purchase_method_data, transaction_card_purchase_suffix_data = (
            extract_transaction_card_purchase_method(transaction=transaction)
        )
        # Build the dictionary of transaction data.
        transaction_data: Dict[str, Any] = {
            "created_at": transaction.created_at,
            "description": transaction.description,
            "amount": transaction.amount,
            "category": transaction_category_data,
            "parent_category": transaction_parent_category_data,
            "tags": transaction_tag_data,
            "message": transaction.message,
            "transaction_id": transaction.id,
            "amount_in_base_units": transaction.amount_in_base_units,
            "card_purchase_method": transaction_card_purchase_method_data,
            "card_purchase_method_card_suffix": transaction_card_purchase_suffix_data,
            "cashback": str(transaction.cashback),
            "foreign_amount": str(transaction.foreign_amount),
            "raw_text": transaction.raw_text,
            "round_up": str(transaction.round_up),
            "status": transaction.status,
            "settled_at": transaction.settled_at,
            "long_description": transaction.long_description,
        }
        all_transactions.append(transaction_data)
    # Convert list of transactions into a dataframe.
    all_transactions_df = pd.DataFrame(all_transactions)
    logger.info(f"Converted {len(all_transactions_df.index)} transactions to Pandas dataframe.")
    return all_transactions_df


def filter_transactions_by_tag(df: pd.DataFrame, tag: str, exact_match: bool = True) -> pd.DataFrame:
    """Filter a pandas dataframe of transactions by a supplied tag.

    Args:
        df: Pandas dataframe of transactions, ready to be filtered.
        tag: The name of the tag to be filtered for. NOTE: Case-sensitive.
        exact_match: Boolean to toggle for exact tag matches (True) or contains tag matches (False)

    Returns:
        df: Pandas dataframe containing transactions with the filtered tags only.
    """
    original_df_length = len(df.index)
    logger.debug(f"Filtering for tag: '{tag}' in {original_df_length} in transactions.")
    # When the exact_match boolean is supplied only filter for exact entries, else do a contains filter.
    # Example of a contains filter:
    # A tag of "fuel" would match BOTH tags in the dataframe column of "Car fuel" and "Truck fuel"
    df = df[df["tags"] == tag] if exact_match else df[df["tags"].str.contains(tag)]
    final_df_length = len(df.index)
    logger.info(f"Discovered {final_df_length} transactions with the tag: {tag}")
    return df


def filter_transactions_by_withdrawals_only(df: pd.DataFrame) -> pd.DataFrame:
    """Filter a pandas dataframe of transactions for withdrawals only.

    Args:
        df: Pandas dataframe of transactions, ready to be filtered.

    Returns:
        df: Pandas dataframe containing transactions which are only withdrawals.
    """
    original_df_length = len(df.index)
    logger.debug(f"Filtering {original_df_length} for withdrawals")
    df = df[df["amount"] < 0.0]
    final_df_length = len(df.index)
    logger.info(
        f"Discovered {final_df_length} withdrawal transactions from {original_df_length} total transactions, "
        f"removed {original_df_length - final_df_length} deposit transactions."
    )
    return df


def filter_transactions_with_empty_tag(df: pd.DataFrame) -> pd.DataFrame:
    """Filter a pandas dataframe of transactions which have no tag.

    Args:
        df: Pandas dataframe of transactions, ready to be filtered.

    Returns:
        df: Pandas dataframe containing transactions which have no tags..
    """
    original_df_length = len(df.index)
    logger.debug(f"Filtering {original_df_length} for untagged transactions.")
    df = df[(df["tags"].isnull()) | (df["tags"].str.len() == 0)]
    final_df_length = len(df.index)
    logger.info(
        f"Discovered {final_df_length} untagged transactions from {original_df_length} total transactions, "
        f"removed {original_df_length - final_df_length} tagged transactions."
    )
    return df


def check_whether_budget_exceeds_variance(spend_value: float, upper_variance_limit: float) -> str:
    """Check whether a value exceeds a variance, and return a string which indicates the result.

    Args:
        spend_value: The percentage value which has been spent.
            Example(s):
                120.10
                103.13
                "" - An empty value which didn't have a percentage spend value. This would be an unbudgeted tag.
        upper_variance_limit: The upper variance limit percentage, which when breached which constitute a breach
            Example: 110.0

    Returns:
        variance_breach: String which indicates a variance breach.
            Example(s) based on above:
                120.10 - "YES"
                103.13 - "NO"
                "" - "N/A"
    """
    variance_breach: str = ""
    if isnan(spend_value):
        variance_breach = "N/A"
    elif spend_value >= upper_variance_limit:
        variance_breach = "YES"
    else:
        variance_breach = "NO"
    return variance_breach


def check_whether_spend_under_accepted_variance(spend_value: float, lower_variance_limit: float) -> str:
    """Check whether a value is under an acceptance variance, and return a string which indicates the result.

    Args:
        spend_value: The percentage value which has been spent.
            Example(s):
                98.30
                91.45
                "" - An empty value which didn't have a percentage spend value. This would be an unbudgeted tag.
        lower_variance_limit: The lower variance limit percentage, which when not met which constitute a breach
            Example: 92.5

    Returns:
        variance_breach: String which indicates a variance breach.
            Example(s) based on above:
                98.30 - "NO"
                91.45 - "YES"
                "" - "N/A"
    """
    variance_breach: str = ""
    if isnan(spend_value):
        variance_breach = "N/A"
    elif spend_value <= lower_variance_limit:
        variance_breach = "YES"
    else:
        variance_breach = "NO"
    return variance_breach


def calculate_weekly_budget_variance(
    df: pd.DataFrame, upper_variance_limit: float = 120.00, lower_variance_limit: float = 97.50
) -> pd.DataFrame:
    """Calculate the variance between a each tags' budget and it's actual spend and amend the results to the dataframe.

    Args:
        df: Pandas dataframe which contains the weekly spend and weekly budget data.
        upper_variance_limit: The upper variance limit, which when breached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 120.00.
        lower_variance_limit: The upper variance limit, which not reached by a tag, constitutes a budget variance
        breach which is worth investigation.
            Defaults to 97.50.

    Returns:
        df: Pandas dataframe with the variance analysis.
    """
    df["weekly_spend"] = df["weekly_spend"].astype(float)
    df["weekly_budget"] = df["weekly_budget"].astype(float)
    df["weekly_budget_variance"] = df["weekly_spend"] / df["weekly_budget"] * 100
    df["weekly_budget_variance"] = df["weekly_budget_variance"].astype(float)
    df["exceeds_variance"] = df["weekly_budget_variance"].apply(
        lambda x: check_whether_budget_exceeds_variance(spend_value=x, upper_variance_limit=upper_variance_limit)
    )
    df["under_variance"] = df["weekly_budget_variance"].apply(
        lambda x: check_whether_spend_under_accepted_variance(spend_value=x, lower_variance_limit=lower_variance_limit)
    )
    df = df.sort_values(by=["weekly_budget"], ascending=False)
    return df
