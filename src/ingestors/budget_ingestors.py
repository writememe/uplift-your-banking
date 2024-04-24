"""Budget ingestors."""

import json
import os
from typing import Any, Dict, List

import pandas as pd

from src.shared.logging.logger import InternalLogger  # noqa
from src.shared.settings import DEFAULT_LOG_FILE

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="budget_ingestors")


def load_json_budget_to_df(input_dir: str, input_filename: str) -> pd.DataFrame:
    """Load a JSON file which contains a list of tags and the 'weekly_budget' amount.

    Args:
        input_dir: The input directory which contains budget file.
        input_filename: The input JSON filename.

    Returns:
        df: The pandas dataframe containing the budget data.
    """
    budget_file_path = os.path.join(input_dir, input_filename)
    if not (os.path.exists(budget_file_path)):
        error_message = f"File path doesnt exist: {budget_file_path}. Please check your inputs and try again."
        logger.critical(error_message)
        raise FileNotFoundError(error_message)
    with open(budget_file_path) as budget_file:
        budget_data: List[Dict[str, Any]] = json.load(budget_file)
    df = pd.DataFrame(budget_data)
    logger.info(f"Budget Data: {df.head}")
    return df


def load_csv_budget_to_df(input_dir: str, input_filename: str) -> pd.DataFrame:
    """Load a CSV file which contains a list of tags and the 'weekly_budget' amount..

    Args:
        input_dir: The input directory which contains budget file.
        input_filename: The input CSV filename.

    Returns:
        _df: The pandas dataframe containing the budget data.
    """
    budget_file_path = os.path.join(input_dir, input_filename)
    if not (os.path.exists(budget_file_path)):
        error_message = f"File path doesnt exist: {budget_file_path}. Please check your inputs and try again."
        logger.critical(error_message)
        raise FileNotFoundError(error_message)
    with open(budget_file_path) as budget_file:
        df = pd.read_csv(filepath_or_buffer=budget_file)
    logger.info(f"Budget Data: {df.head}")
    return df
