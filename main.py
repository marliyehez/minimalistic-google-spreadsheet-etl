import os
from functions import (
    get_month_and_month_num, fetch_and_prepare_data, get_recap_worksheet,
    etl_student_data, etl_fee_data)
from logger_config import setup_logger

from dotenv import load_dotenv
load_dotenv()
# Load environment variables
sheet_url = os.getenv("sheet_url")
service_account_path = os.getenv("service_account_path")
recap_sheet_title = os.getenv("recap_sheet_title")

# Setup logger
logger = setup_logger(__name__)

def main() -> None:
    try:
        # Get the number of month
        # (and also month name if 'month' is None)
        month, month_num = get_month_and_month_num()

        # Fetch data and prepare it for processing
        cleaned_df = fetch_and_prepare_data(sheet_url, month)

        # Get the worksheet where data will be written
        worksheet = get_recap_worksheet(sheet_url, recap_sheet_title, service_account_path)
        
        # Execute ETL processes for student and fee data
        etl_student_data(cleaned_df, worksheet, month, month_num)
        etl_fee_data(cleaned_df, worksheet, month, month_num)

        # Log success message
        logger.info(f"Status: {month} data is successfully updated")
    
    except Exception as e:
        # Log error message
        logger.error(f"An error occurred: {e}")
        logger.error("", exc_info=True)

if __name__ == '__main__':
    main()