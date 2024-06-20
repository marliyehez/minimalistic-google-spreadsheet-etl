import pandas as pd
from .common_utils import add_month_columns, join_non_empty_strings

def get_student_config() -> dict:
    '''
    Imports the ETL configuration settings for student data
    from the `etl_student` configuration file and returns them as a dictionary.
    '''
    from config.etl_student import start_cell, end_col, null_check_max_row, int_cols
    kwargs = {
        'start_cell': start_cell,
        'end_col': end_col,
        'null_check_max_row': null_check_max_row,
        'int_cols': int_cols
    }
    return kwargs


def calculate_student_aggregate(
        cleaned_df: pd.DataFrame,
        month: str,
        month_num: int
    ) -> pd.DataFrame:
    '''
    Performs various aggregations on the cleaned student data to 
    compute totals and counts of specific categories (e.g., new students, dropouts,
    students on leave, and unpaid fees) grouped by instrument. It also records the
    names of students in each category and adds the month and month number columns
    to the result.
    '''
    # Total murid
    res_murid = cleaned_df \
        .groupby('instrument', as_index=False) \
        .size() \
        .rename(columns={'size': 'total'})

    # Perhitungan murid sesuai kriteria
    res_murid = res_murid.merge(
        cleaned_df
            .groupby('instrument', as_index=False)
            .agg({
                'is_baru': 'sum',
                'is_keluar': 'sum',
                'is_cuti': 'sum',
                'not_lunas': 'sum'
            })
        ,
        how='left',
        on='instrument'
    )

    # Pendataan nama murid
    cols = ['is_baru', 'is_keluar', 'is_cuti', 'not_lunas']
    for col in cols:
        res_murid = res_murid.merge(
            cleaned_df[cleaned_df[col] == 1]
                .groupby('instrument', as_index=False)
                .agg({'nama': join_non_empty_strings})
                .rename(columns={'nama': f'nama_{col}'})
            ,
            how='left',
            on='instrument'
        )

    res_murid = add_month_columns(res_murid, month, month_num)
    return res_murid.fillna(' ')