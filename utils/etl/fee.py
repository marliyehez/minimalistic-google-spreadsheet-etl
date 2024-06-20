import pandas as pd
from .common_utils import add_month_columns

def get_fee_config() -> dict:
    '''
    Imports configuration variables from the `config.etl_fee` module and 
    initializes a dictionary with these variables.
    '''
    from config.etl_fee import start_cell, end_col, null_check_max_row, int_cols
    kwargs = {
        'start_cell': start_cell,
        'end_col': end_col,
        'null_check_max_row': null_check_max_row,
        'int_cols': int_cols
    }
    return kwargs


def calculate_fee_aggregate(
        cleaned_df: pd.DataFrame,
        month: str,
        month_num: int
    ) -> pd.DataFrame:
    '''
    Performs ETL operations to aggregate fee data. It groups the cleaned 
    DataFrame by 'instrument' and calculates the sum of 'biaya_spp' and 'biaya_regis'. 
    It then adds month and month number columns to the resulting DataFrame.
    '''
    agg_biaya = {'biaya_spp': 'sum', 'biaya_regis': 'sum'}
    res_biaya = cleaned_df \
        .groupby('instrument', as_index=False) \
        .agg(agg_biaya)

    res_biaya = add_month_columns(res_biaya, month, month_num)
    return res_biaya