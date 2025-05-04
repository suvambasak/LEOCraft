
'''
Generate a traffic matrix based on the population and GDP of the cities
'''

import json

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


def create_population_weighted_traffic_matrix():
    'Create a population weighted traffic matrix'

    df = pd.read_csv(RAW_TM_GS_CSV)

    # Target market 10% of the city population
    df['pop'] = df['pop'] * 10 // 100

    # Assuming 300 Kbps data rate per head
    df['traffic'] = df['pop'] * BASE_DATA_RATE_KBPS

    traffic_metrics = dict()

    for src in df.itertuples(index=True, name='Src'):

        # Sum of geodesic distance inverse from the source to all other destinations
        sum_all_geodesic_inverse = sum([
            1/geodesic_distance_km(
                src.lat,
                src.lng,
                _dst.lat,
                _dst.lng
            ) for _dst in df.itertuples(
                index=True, name='Dst'
            ) if _dst.id != src.id
        ])

        for dst in df.itertuples(index=True, name='Dst'):

            if src.id == dst.id:
                continue

            geodesic_inverse = 1 / geodesic_distance_km(
                src.lat,
                src.lng,
                dst.lat,
                dst.lng
            )

            # Traffic metric for the source-destination pair in Gbps
            traffic_metrics[f'G-{src.id}_G-{dst.id}'] = (
                src.traffic * (geodesic_inverse / sum_all_geodesic_inverse)
            )/1000000

    with open(TRAFFIC_MATRIX_JSON, 'w') as json_file:
        json_file.write(json.dumps(traffic_metrics, indent=2))


def create_population_and_GDP_weighted_traffic_matrix():
    'Create a population and GDP weighted traffic matrix'

    df = pd.read_csv(RAW_TM_GS_CSV)

    # Target market 10% of the city population
    df['pop'] = df['pop'] * 10 // 100

    TOTAL_POPULATION = df['pop'].sum()
    TOTAL_GDP = df['gdp'].sum()

    # Add population and GDP weighted columns
    # Traffic demand assuming 300 Kbps data rate per head
    df['weight'] = (df['gdp'] / TOTAL_GDP) * TOTAL_POPULATION
    df['traffic'] = df['weight'] * BASE_DATA_RATE_KBPS

    traffic_metrics = dict()
    for src in df.itertuples(index=True, name='Src'):

        # Sum of geodesic distance inverse from the source to all other destinations
        sum_all_geodesic_inverse = sum([
            1/geodesic_distance_km(
                src.lat,
                src.lng,
                _dst.lat,
                _dst.lng
            ) for _dst in df.itertuples(
                index=True, name='Dst'
            ) if _dst.id != src.id
        ])

        for dst in df.itertuples(index=True, name='Dst'):

            if src.id == dst.id:
                continue

            geodesic_inverse = 1 / geodesic_distance_km(
                src.lat,
                src.lng,
                dst.lat,
                dst.lng
            )

            # Traffic metric for the source-destination pair in Gbps
            traffic_metrics[f'G-{src.id}_G-{dst.id}'] = (
                src.traffic * (geodesic_inverse / sum_all_geodesic_inverse)
            )/1000000

    with open(TRAFFIC_MATRIX_JSON, 'w') as json_file:
        json_file.write(json.dumps(traffic_metrics, indent=2))


if __name__ == "__main__":

    # Input CSV file
    # RAW_TM_GS_CSV = 'dataset/src/ground_stations/CSVs/preprocess/RAW_TM_GS_100.csv'
    RAW_TM_GS_CSV = 'dataset/src/ground_stations/CSVs/preprocess/RAW_TM_GS_1000.csv'

    # Output JSON file
    TRAFFIC_MATRIX_JSON = 'traffic_matrix.json'

    BASE_DATA_RATE_KBPS = 300

    create_population_weighted_traffic_matrix()
    # create_population_and_GDP_weighted_traffic_matrix()
