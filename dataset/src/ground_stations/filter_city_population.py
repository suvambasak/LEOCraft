
'''
Filter the population of cities from the worldcities.csv dataset
and find the closest city when name do not macth.
'''

import sys

import pandas as pd
from geopy.distance import great_circle


def geodesic_distance_km(
    lat_1: float,
    lng_1: float,

    lat_2: float,
    lng_2: float
) -> float:
    'Calculate the geodesic distance in kilometers between two points on the Earth'

    EARTH_RADIOUS_KM = 6378.135

    return great_circle(
        (float(lat_1), float(lng_1)),
        (float(lat_2), float(lng_2)),
        radius=EARTH_RADIOUS_KM
    ).km


def find_closest_city(city_info, df_all_cities: pd.DataFrame) -> tuple[str, float, float]:
    'Find the closest city to the given city information in the DataFrame'

    min_distance = sys.maxsize
    closest_city = None

    for row in df_all_cities.itertuples(index=True, name='City'):

        current_distance = geodesic_distance_km(
            city_info.latitude_degree,
            city_info.longitude_degree,
            row.lat,
            row.lng
        )

        if current_distance < min_distance:
            min_distance = current_distance
            closest_city = row

    return closest_city.city, closest_city.population, min_distance


def find_population_by_city_name():
    'Find the population of a city by its name in the DataFrame'

    df_all_cities = pd.read_csv(ALL_CITIES_CSV)
    df_few_cities = pd.read_csv(FEW_CITIES_CSV)

    # Convert the city names to lowercase for case-insensitive comparison
    df_all_cities['lcity'] = df_all_cities['city'].str.lower()
    df_all_cities['lcity_ascii'] = df_all_cities['city_ascii'].str.lower()
    df_few_cities['lname'] = df_few_cities['name'].str.lower()

    # Record the population of the cities
    population_dataset = list()

    for row in df_few_cities.itertuples(index=True, name='City'):

        # Find by city name and city name ascii
        result_city = df_all_cities.loc[
            df_all_cities['lcity'] == row.lname
        ]
        result_city_ascii = df_all_cities.loc[
            df_all_cities['lcity_ascii'] == row.lname
        ]

        population_record = {'name_1': row.name, 'distance_km': 0.0}

        if not result_city.empty:
            population_record['name_2'] = result_city.iloc[0]['city']
            population_record['population'] = result_city.iloc[0]['population']
            print(
                f'|- [{row.id}] {row.name}:{result_city.iloc[0]["city"]} {result_city.iloc[0]["population"]}'
            )

        elif not result_city_ascii.empty:
            population_record['name_2'] = result_city_ascii.iloc[0]['city_ascii']
            population_record['population'] = result_city_ascii.iloc[0]['population']
            print(
                f'|- [{row.id}] {row.name}:{result_city_ascii.iloc[0]["city_ascii"]} {result_city_ascii.iloc[0]["population"]}'
            )

        else:
            city_name, city_population, min_distance = find_closest_city(
                row, df_all_cities
            )

            print(
                f'|x [{row.id}] {row.name}: [closest] : {city_name} {city_population} ## {min_distance:.2f} km'
            )

            # When the population is not found, ask the user for input
            if pd.isna(city_population):
                city_population = input(
                    f'|xx [{row.id}] {row.name}: [closest] : {city_name} POPULATION?: '
                )

            population_record['name_2'] = city_name
            population_record['population'] = city_population
            population_record['distance_km'] = 0.0

        population_dataset.append(population_record)

    pd.DataFrame(
        population_dataset
    ).to_csv(POPULATION_CSV, index=False)


if __name__ == '__main__':

    # Input CSV files
    ALL_CITIES_CSV = 'dataset/src/ground_stations/CSVs/raw/worldcities.csv'
    # FEW_CITIES_CSV = 'dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv'
    FEW_CITIES_CSV = 'dataset/ground_stations/cities_sorted_by_estimated_2025_pop_top_1000.csv'

    # Output CSV file
    # POPULATION_CSV = 'dataset/src/ground_stations/CSVs/preprocess/POPULATION_100.csv'
    POPULATION_CSV = 'dataset/src/ground_stations/CSVs/preprocess/POPULATION_1000.csv'

    find_population_by_city_name()
