import pandas as pd
from gspread import Worksheet

import re
from typing import Optional, Tuple, List

def get_spreadsheet_table(worksheet: Worksheet, **kwargs) -> pd.DataFrame:
    '''
    Extracts a specified range of cells from a Google Sheets worksheet
    based on provided starting cell, ending column, and a range to check for null values.
    It converts the extracted data into a Pandas DataFrame.
    '''
    # Extract variable from kwargs
    start_cell: str = kwargs.get('start_cell')
    end_col: str = kwargs.get('end_col')
    null_check_max_row: int = kwargs.get('null_check_max_row')

    # Get spreadsheet table range
    start_col, start_row = split_letters_numbers(start_cell)
    check_null_range = f'{start_cell}:{start_col}{null_check_max_row}'
    end_row = detect_end_row(worksheet, check_range=check_null_range)
    tabel_range = f'{start_cell}:{end_col}{end_row}'

    # Get spreadsheet table
    data = worksheet.get(tabel_range)
    columns = data[0]
    data = data[1:]
    
    # Convert to DataFrame
    # for row in data:
    #     if len(row) < len(columns):
    #         row.extend("" * (13 - len(row)))
    df = pd.DataFrame(data, columns=columns)

    return df


def update_to_spreadsheet_worksheet(
        worksheet:Worksheet,
        df: pd.DataFrame,
        **kwargs
    ) -> None:
    '''
    Updates the specified worksheet with the data from a DataFrame,
    starting from a specified cell.
    '''
    # Extract variable from kwargs
    start_cell: str = kwargs.get('start_cell')

    # Start cell for table's values (rows under the column row)
    values_start_col = split_letters_numbers(start_cell)[0]
    values_start_row = split_letters_numbers(start_cell)[1] + 1
    values_start_cell = f'{values_start_col}{values_start_row}'

    # Update table to the worksheet
    worksheet.update([list(df)], start_cell)
    worksheet.update(df.values.tolist(), values_start_cell)


def split_letters_numbers(input_str: str) -> Optional[Tuple[str, int]]:
    '''
    Splits a string into its alphabetical and numerical parts,
    returning them as a tuple.
    '''
    match = re.match(r"([a-zA-Z]+)(\d+)", input_str)
    if match:
        letters = match.group(1)
        numbers = int(match.group(2))
        return letters, numbers
    else:
        return None


def detect_end_row(worksheet: Worksheet, check_range: str) -> Optional[int]:
    '''
    Checks a range of cells in a worksheet and returns the row number
    of the last non-empty cell.
    '''
    range_to_check = worksheet.range(check_range)
    for cell in range_to_check:
        if not cell.value:
            return cell.row - 1
    return


def fix_int_columns_dtype(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    '''
    Converts the data type of specified columns in a DataFrame to integers.
    '''
    # Extract variable from kwargs
    int_cols: List[str] = kwargs.get('int_cols')
    
    # Transform types
    for col in int_cols:
        df[col] = df[col].astype(int)
    return df


def add_month_columns(
        df: pd.DataFrame,
        month: str,
        month_num: int
    ) -> pd.DataFrame:
    '''
    Inserts 'month' and 'month_num' columns at the beginning of a DataFrame.
    '''
    df.insert(0, 'month', month)
    df.insert(0, 'month_num', month_num)

    return df


def join_non_empty_strings(strings: List) -> str:
    '''
    Takes a list of strings and joins the non-empty ones with commas.
    '''
    non_empty_strings = [s for s in strings if s]
    return ', '.join(non_empty_strings)


def update_by_month(old_df: pd.DataFrame, updated_df: pd.DataFrame, month_num: int):
    '''
    Drops rows corresponding to a specified month number from the old DataFrame
    and appends the new updated DataFrame, then sorts the result by the month number.
    '''
    drop_index = old_df[old_df['month_num'] == month_num].index

    return (
        pd.concat([old_df.drop(drop_index), updated_df])
        .sort_values('month_num', ignore_index=True)
    )