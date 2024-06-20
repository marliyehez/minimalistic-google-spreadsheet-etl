import gspread
import pandas as pd
import unittest.mock as mock

from utils.etl.common_utils import (
    split_letters_numbers,
    detect_end_row,
    fix_int_columns_dtype,
    add_month_columns,
    join_non_empty_strings,
    update_by_month,
)

class Cell:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value


def test_split_letters_numbers():
    assert split_letters_numbers("A1") == ("A", 1)
    assert split_letters_numbers("BC12") == ("BC", 12)
    assert split_letters_numbers("XYZ987") == ("XYZ", 987)
    assert split_letters_numbers("123") is None
    assert split_letters_numbers("ABC") is None


@mock.patch('gspread.Worksheet.range')
def test_detect_end_row(mock_range):
    mock_worksheet = mock.Mock()
    mock_worksheet.range.return_value = [
        Cell(1, 'A', 'ETL Biaya'),
        Cell(2, 'A', 'month_num'),
        Cell(3, 'A', '2'),
        Cell(4, 'A', '3'),
        Cell(5, 'A', '3'),
        Cell(6, 'A', '4'),
        Cell(7, 'A', ''),
        Cell(8, 'A', ''),
        Cell(9, 'A', ''),
        Cell(10, 'A', '')
    ]

    result = detect_end_row(mock_worksheet, 'A1:A10')

    assert result == 6


def test_fix_int_columns_dtype():
    df = pd.DataFrame({"col1": ["1", "2", "3"], "col2": ["4", "5", "6"]})
    int_cols = ["col1", "col2"]
    result_df = fix_int_columns_dtype(df, int_cols=int_cols)

    assert result_df["col1"].dtype == int
    assert result_df["col2"].dtype == int


def test_add_month_columns():
    df = pd.DataFrame({"col1": [1, 2, 3]})
    month = "January"
    month_num = 1
    result_df = add_month_columns(df, month, month_num)

    expected_df = pd.DataFrame({"month_num": [1, 1, 1], "month": ["January", "January", "January"], "col1": [1, 2, 3]})
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_join_non_empty_strings():
    assert join_non_empty_strings(["a", "b", ""]) == "a, b"
    assert join_non_empty_strings(["", "", ""]) == ""
    assert join_non_empty_strings(["hello", "world"]) == "hello, world"


def test_update_by_month():
    old_df = pd.DataFrame({"month_num": [1, 2, 3], "value": ["old1", "old2", "old3"]})
    updated_df = pd.DataFrame({"month_num": [2], "value": ["new2"]})
    result_df = update_by_month(old_df, updated_df, 2)

    expected_df = pd.DataFrame({"month_num": [1, 2, 3], "value": ["old1", "new2", "old3"]})
    pd.testing.assert_frame_equal(result_df, expected_df)