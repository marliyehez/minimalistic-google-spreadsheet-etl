import pandas as pd
import re    

def read_gsheet(sheet_url: str, **kwargs) -> pd.DataFrame:
    '''
    Validates the provided Google Sheets URL, converts it to an exportable
    URL, and reads the data into a Pandas DataFrame.
    '''
    # Validate the input URL
    # https://docs.google.com/spreadsheets/d/1kaci6AtLCpOENLcfJ2RvtgMOph1FcBumvJ2pkRBQhro/edit?usp=sharing
    
    pattern = r'^https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9_-]+\/[a-z]+\?usp=sharing$'
    if not re.match(pattern, sheet_url):
        raise ValueError("The provided URL is not a valid Google Sheets URL.")

    # Convert to the export URL
    id = sheet_url.split('/')[-2]
    converted_url = f"https://docs.google.com/spreadsheets/d/{id}/export?format=xlsx"

    # Read the Excel file into a DataFrame
    try:
        df = pd.read_excel(converted_url, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Failed to read the Google Sheets document: {e}")

    return df


def remove_unnecessary_rows(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Removes rows that contain only NaN values and rows that contain 
    the phrase 'total per bulan'.
    '''
    # Remove rows with NaN values in every of its columns
    df = df.dropna(how='all', ignore_index=True)

    # Remove `total per bulan` rows
    filt = df[3].str.lower().str.contains("total per bulan", na=False)
    df = df.drop(df[filt].index.tolist()).reset_index(drop=True)

    return df


def transform_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Processes the raw data by segmenting it into sub-dataframes
    based on the occurrence of 'teacher' in the first column. It then tidies and 
    cleans each sub-dataframe, adds relevant columns, and concatenates them into a 
    single cleaned DataFrame.
    '''
    # Output cleaned dataframe
    cleaned_df = []

    # Finding boundary index for each `df_sub`
    filt = df[0].str.lower().str.contains("teacher", na=False)
    df_sub_ids = df[filt].index.tolist()
    df_sub_ids.append(len(df))

    # Iterate each `df_sub`
    for i in range(len(df_sub_ids[:-1])):
        # Get teacher and instrument
        top_row = df_sub_ids[i]
        teacher = df.iloc[top_row, 1]
        instrument = df.iloc[top_row+1, 1]

        # Get the sub dataframe
        start = top_row + 2
        end = df_sub_ids[i+1]
        df_sub = df.copy().iloc[start:end].reset_index(drop=True)

        # Tidy it
        df_sub.columns = df_sub.iloc[0].str.lower().str.replace(' ', '_').values
        df_sub = df_sub.drop([0]).reset_index(drop=True)

        # Drop unnecessary column
        df_sub.drop(['no', 'keterangan_tambahan'], axis=1, inplace=True)

        # Add columns for teacher and instrument
        df_sub['instrument'] = instrument
        df_sub['teacher'] = teacher

        # Append it
        cleaned_df.append(df_sub)

    return pd.concat(cleaned_df, ignore_index=True)


def clean_transformed_data(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Fills NaN values, infers the correct data types, and renames columns 
    in the cleaned DataFrame.
    '''
    # Clean NaN
    with pd.option_context("future.no_silent_downcasting", True):
        cleaned_df['biaya_pendaftaran'] = cleaned_df['biaya_pendaftaran'].fillna(0).infer_objects(copy=False)
        cleaned_df['keterangan'] = cleaned_df['keterangan'].fillna('')

    # Rename columns
    cleaned_df.rename(
        columns={'harga': 'biaya_spp', 'biaya_pendaftaran': 'biaya_regis'},
        inplace=True)

    return cleaned_df


def extract_keterangan_columns(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Creates new boolean columns based on the presence of specific keywords 
    in the 'keterangan' column of the DataFrame.
    '''
    cleaned_df['is_trial'] = cleaned_df['keterangan'].apply(lambda x: 1 if 'trial' in x.lower() else 0)

    cleaned_df['is_baru'] = cleaned_df['keterangan'].apply(lambda x: 1 if 'baru' in x.lower() else 0)

    cleaned_df['is_keluar'] = cleaned_df['keterangan'].apply(lambda x: 1 if 'keluar' in x.lower() else 0)

    cleaned_df['is_cuti'] = cleaned_df['keterangan'].apply(lambda x: 1 if 'cuti' in x.lower() else 0)

    cleaned_df['not_lunas'] = cleaned_df['keterangan'].apply(lambda x: 0 if 'lunas' in x.lower() else 1)

    return cleaned_df