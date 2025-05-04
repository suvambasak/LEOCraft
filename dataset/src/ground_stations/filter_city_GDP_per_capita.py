
'''
Find the GDP per capita of a city by its name,
Keep the city name and GDP per capita in a CSV file empty when not found.
'''

import pandas as pd


def find_GDP_per_capita_by_city_name():
    'Find the GDP per capita of a city by its name'

    df_few_cities = pd.read_csv(CITIES_CSV)
    df_few_cities['name'] = df_few_cities['name'].str.lower()

    df_all_GDP = pd.read_csv(ALL_GDP_CSV)
    CITY_NAME_LABEL = df_all_GDP.columns[1]
    GDP_PER_CAPITA_LABEL = df_all_GDP.columns[-1]
    df_all_GDP[CITY_NAME_LABEL] = df_all_GDP[CITY_NAME_LABEL].str.lower()

    # Record the population of the cities
    GDP_per_capita_dataset = list()

    for row in df_few_cities.itertuples(index=True, name='City'):

        # Create a record for each city
        GDP_per_capita_record = {'name_1': row.name}

        result = df_all_GDP.loc[
            df_all_GDP[CITY_NAME_LABEL] == row.name
        ]

        if not result.empty:
            GDP_per_capita_record['name_2'] = result.iloc[0][CITY_NAME_LABEL]
            GDP_per_capita_record['GDP_per_capita'] = float(result.iloc[0][GDP_PER_CAPITA_LABEL].replace(
                ',', ''))
            print(
                f'|- {row.name}:{result.iloc[0][CITY_NAME_LABEL]} {result.iloc[0][GDP_PER_CAPITA_LABEL]}'
            )

        else:
            GDP_per_capita_record['name_2'] = None
            GDP_per_capita_record['GDP_per_capita'] = 'MANUALLY_SET'
            print(
                f'|x {row.name}: Not Found'
            )

        GDP_per_capita_dataset.append(GDP_per_capita_record)

    pd.DataFrame(
        GDP_per_capita_dataset
    ).to_csv(GDP_PER_CAPITA_OF_CITIES_CSV, index=False)


if __name__ == '__main__':

    # Input CSV files
    ALL_GDP_CSV = 'dataset/src/ground_stations/CSVs/raw/List_of_cities_by_GDP_2.csv'
    CITIES_CSV = 'dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv'

    # Output CSV file
    GDP_PER_CAPITA_OF_CITIES_CSV = 'dataset/src/ground_stations/CSVs/preprocess/GDP_PER_CAPITA_100.csv'

    # CITIES_CSV = 'dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_1000.csv'
    # GDP_PER_CAPITA_OF_CITIES_CSV = 'dataset/src/CSVs/GDP_per_capita_1000.csv'

    find_GDP_per_capita_by_city_name()
