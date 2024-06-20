import pytest
import pandas as pd
# from unittest.mock import patch
from utils.create_clean_data import read_gsheet, remove_unnecessary_rows

@pytest.mark.parametrize(
    "sheet_url, expected_exception",
    [
        ("invalid_url", ValueError),  # Invalid URL format
        ("https://docs.google.com/spreadsheets/d/sheet_id/edit", ValueError),  # no usp
        ("https://docs.google.com/spreadsheets/d/sheet_id/?usp=sharing", ValueError),  # no access (edit/view)
        ("https://docs.google.com/spreadsheets/d//edit?usp=sharing", ValueError),  # no sheet id
    ],
)
def test_invalid_url(sheet_url, expected_exception):
    with pytest.raises(expected_exception):
        read_gsheet(sheet_url)

def test_remove_unnecessary_rows():
    data = {
        0: [1, 2, None, 4],
        1: ["a", "b", None, "d"],
        2: ["apple", None, "orange", None],
        3: ["empty", None, "total per bulan", "empty"]
    }


    df = pd.DataFrame(data)
    result_df = remove_unnecessary_rows(df.copy())
    print(result_df)
    print('--')
    expected_df = pd.DataFrame(
        {
            0: [1.0, 2.0, 4.0],
            1: ["a", "b", "d"],
            2: ["apple", None, None],
            3: ["empty", None, "empty"],
        }
    )
    print(expected_df)

    pd.testing.assert_frame_equal(result_df, expected_df)