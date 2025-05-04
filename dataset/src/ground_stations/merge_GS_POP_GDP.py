
'''
This script merges the ground station data with population and GDP data.
'''

import pandas as pd


def get_record(df: pd.DataFrame, key: str, label: str) -> dict:
    'Get the record from the dataframe based on the key.'
    record = df.loc[df['name_1'].str.lower() == key.lower()]
    assert len(record) != 0
    return record.iloc[0].to_dict().get(label)


def merge_records():
    'Merge the records from the three dataframes.'
    df_GS = pd.read_csv(GS_CSV)
    df_POP = pd.read_csv(POPULATION_CSV)
    # df_GDP = pd.read_csv(GDP_CSV)

    pd.DataFrame(
        [{
            'id': row.id,
            'name': row.name,
            'lat': row.latitude_degree,
            'lng': row.longitude_degree,
            'pop': get_record(df_POP, row.name, 'population'),
            # 'gdp': get_record(df_GDP, row.name, 'GDP_per_capita') * get_record(df_POP, row.name, 'population')
        } for row in df_GS.itertuples(index=True, name='Record')]
    ).to_csv(OUTPUT_CSV, index=False)


if __name__ == "__main__":

    # Input CSV files
    # GS_CSV = 'dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv'
    GS_CSV = 'dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_1000.csv'

    # POPULATION_CSV = 'dataset/src/ground_stations/CSVs/preprocess/POPULATION_100.csv'
    POPULATION_CSV = 'dataset/src/ground_stations/CSVs/preprocess/POPULATION_1000.csv'

    # GDP_CSV = 'dataset/src/ground_stations/CSVs/preprocess/GDP_PER_CAPITA_100.csv'

    # Output CSV file
    # OUTPUT_CSV = 'dataset/src/ground_stations/CSVs/preprocess/RAW_TM_GS_100.csv'
    OUTPUT_CSV = 'dataset/src/ground_stations/CSVs/preprocess/RAW_TM_GS_1000.csv'

    merge_records()
