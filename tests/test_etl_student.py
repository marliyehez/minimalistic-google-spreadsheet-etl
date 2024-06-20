import pandas as pd
from utils.etl.student import calculate_student_aggregate

def test_calculate_student_aggregate():
    data = {
        'instrument': ['piano', 'piano', 'guitar', 'guitar'],
        'is_trial': [1, 0, 0, 1],
        'is_baru': [1, 1, 0, 1],
        'is_keluar': [0, 1, 0, 0],
        'is_cuti': [0, 0, 1, 0],
        'not_lunas': [0, 0, 1, 1],
        'nama': ['Alice', 'Bob', 'Charlie', 'Dave']
    }

    df = pd.DataFrame(data)
    month = 'January'
    month_num = 1

    result = calculate_student_aggregate(df, month, month_num)

    expected_data = {
        'month_num': [1, 1],
        'month': ['January', 'January'],
        'instrument': ['guitar', 'piano'],
        'total': [2, 2],
        'is_trial': [1, 1],
        'is_baru': [1, 2],
        'is_keluar': [0, 1],
        'is_cuti': [1, 0],
        'not_lunas': [2, 0],
        'nama_is_trial': ['Dave', 'Alice'],
        'nama_is_keluar': ['', 'Bob'],
        'nama_is_cuti': ['Charlie', ''],
        'nama_not_lunas': ['Charlie, Dave', '']
    }
    expected_df = pd.DataFrame(expected_data).fillna('')

    pd.testing.assert_frame_equal(result, expected_df)
