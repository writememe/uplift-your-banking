from src.shared.logging.logger import InternalLogger  # noqa
from src.shared.settings import DEFAULT_LOG_FILE, OUTPUT_DIR
import pandas as pd
import os
from typing import Dict

# Setting logging level to informational
log_level = "INFO"
logger = InternalLogger(log_level=log_level, log_file_name=DEFAULT_LOG_FILE, app_name="exporters")


def export_to_csv(
    df: pd.DataFrame,
    file_name: str = "data.csv",
    output_dir: str = OUTPUT_DIR,
    index: bool = False,
) -> str:
    """Export Pandas dataframe to a CSV file.

    Args:
        df: The pandas dataframe to be exported.
        file_name: The name of the CSV file where the Pandas dataframe will be saved to.
        output_dir: The output directory of the CSV file where the Pandas dataframe will be saved
        to.
        index: Toggle whether the index is True or False

    Returns:
        file_path: The fully abstracted path to the CSV file.

    Raises:
        N/A
    """
    file_path = os.path.abspath(os.path.join(output_dir, file_name))
    df.to_csv(file_path, index=index)
    logger.info(f"CSV file saved to: {file_path}")
    return file_path


def output_dfs_to_excel(
    df_list: Dict[str, pd.DataFrame], output_dir: str = OUTPUT_DIR, filename: str = "example_file.xlsx"
) -> str:
    """Save a list of pandas dataframes to an Excel workbook.

    Args:
        df_list: Key-value representation of the worksheet_name and the pandas dataframe to be saved to the workbook.
        output_dir: The output directory of where the Excel file will be saved.
            Defaults to dirname.
        filename: The name of the Excel file.
            Defaults to "example_file.xlsx".

    Returns:
        excel_file: The location of the Excel file.
    """
    # Assign Excel file a variable name
    excel_file = os.path.join(output_dir, filename)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
    # Iterate over worksheet name (the dict key) and the pandas dataframe (the dict value) and
    # save the dataframe to a new worksheet
    for worksheet_name, df in df_list.items():
        logger.info(f"Saving worksheet: {worksheet_name}")
        df.to_excel(writer, sheet_name=worksheet_name, index=False)
    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
    # Diagnostic printout
    logger.info(f"Excel results are available at: {excel_file}")
    return excel_file
