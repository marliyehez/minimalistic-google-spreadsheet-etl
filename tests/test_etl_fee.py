import pandas as pd
from utils.etl.fee import calculate_fee_aggregate

def test_calculate_fee_aggregate():
    data = {
        'instrument': ['instr1', 'instr2', 'instr1'],
        'biaya_spp': [100, 200, 300],
        'biaya_regis': [50, 75, 125]
    }
    df = pd.DataFrame(data)
    month = 'January'
    month_num = 1

    result = calculate_fee_aggregate(df, month, month_num)

    expected_data = {
        'month_num': [1, 1],
        'month': ['January', 'January'],
        'instrument': ['instr1', 'instr2'],
        'biaya_spp': [400, 200],
        'biaya_regis': [175, 75]
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df, check_dtype=False)