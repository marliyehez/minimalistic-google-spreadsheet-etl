import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

import os
from datetime import datetime
from typing import Tuple

from utils.create_clean_data import read_gsheet, remove_unnecessary_rows, transform_raw_data, clean_transformed_data, extract_keterangan_columns
from utils.etl.student import calculate_student_aggregate, get_student_config
from utils.etl.fee import calculate_fee_aggregate, get_fee_config
from utils.etl.common_utils import get_spreadsheet_table, fix_int_columns_dtype, update_by_month, update_to_spreadsheet_worksheet

def get_month_and_month_num() -> Tuple[str, int]: # belum ada unit testnya
    '''
    Retrieves the current month name and its numeric representation.
    If an environment variable 'month' is set, it returns that month's name and number.
    Otherwise, it returns the current month name and number based on the current date.
    '''
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November",
        "Desember"]
    
    month = os.getenv("month")
    if month:
        month_num = months.index(month) + 1
        return month, month_num
    
    
    month_num = datetime.now().month
    month = months[month_num - 1]
    return month, month_num


def fetch_and_prepare_data(sheet_url: str, month: str) -> pd.DataFrame:
    '''
    Reads data from a Google Sheet for the specified month,
    removes unnecessary rows, and performs a series of transformations to clean the data.
    '''
    # Reading Google Sheet
    df = read_gsheet(sheet_url, engine='openpyxl', sheet_name=month, header=None)

    # Remove unnescessary rows
    df = remove_unnecessary_rows(df)

    # Transform raw data
    cleaned_df = transform_raw_data(df)
    cleaned_df = clean_transformed_data(cleaned_df)
    cleaned_df = extract_keterangan_columns(cleaned_df)
    return cleaned_df


def get_recap_worksheet(
        sheet_url: str,
        recap_sheet_tile: str,
        service_account_path: str
    ) -> gspread.Worksheet:
    '''
    Sets up a Google Sheets API client using a service account,
    and retrieves the 'Recap' worksheet from the specified Google Sheet.
    '''
    # Setting up client
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(service_account_path, scopes=scopes)
    client = gspread.authorize(creds)

    # Getting the 'Recap' worksheet
    sheet_id = sheet_url.split('/')[-2]
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(recap_sheet_tile)
    return worksheet


def etl_student_data(
        cleaned_df: pd.DataFrame,
        worksheet: gspread.Worksheet,
        month: str,
        month_num: int
    ) -> pd.DataFrame:
    '''
    Extracts student data from the cleaned DataFrame, 
    transforms it based on the current month, and loads the updated data 
    into a Google Sheet's worksheet.
    '''
    # Get student's ETL configuration
    student_config = get_student_config()
    
    # Get spreadsheet table 'old_df'
    old_df = get_spreadsheet_table(worksheet, **student_config)

    # Column dtypes
    old_df = fix_int_columns_dtype(old_df, **student_config)

    # ETL (Get new/updated data)
    res_murid = calculate_student_aggregate(cleaned_df, month, month_num)

    # Update with old data
    updated_murid = update_by_month(old_df=old_df, updated_df=res_murid, month_num=month_num)

    # Update to google spreadsheet's worksheet
    update_to_spreadsheet_worksheet(worksheet, updated_murid, **student_config)


def etl_fee_data(
        cleaned_df: pd.DataFrame,
        worksheet: gspread.Worksheet,
        month: str,
        month_num: int
    ) -> pd.DataFrame:
    # Get fee's ETL configuration
    fee_config = get_fee_config()

    # Get spreadsheet table 'old_df'
    old_df = get_spreadsheet_table(worksheet, **fee_config)

    # Column dtypes
    old_df = fix_int_columns_dtype(old_df, **fee_config)

    # ETL (Get new/updated data)
    res_murid = calculate_fee_aggregate(cleaned_df, month, month_num)

    # Update with old data
    updated_murid = update_by_month(old_df=old_df, updated_df=res_murid, month_num=month_num)

    # Update to google spreadsheet's worksheet
    update_to_spreadsheet_worksheet(worksheet, updated_murid, **fee_config)