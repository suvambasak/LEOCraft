
'''
Generate a traffic matrix based on the population and passengers in flights
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

    df_GS = pd.read_csv(RAW_TM_GS_CSV)
    df_proxy_GS = pd.read_csv(FLIGHT_PROXY_GS_CSV)

    # Target market 10% of the city population and 50% of the passengers
    df_GS['pop'] = df_GS['pop'] * 10 // 100
    df_proxy_GS['pop'] = df_proxy_GS['pop'] * 50 // 100

    # Assuming 300 Kbps data rate per head
    df_GS['traffic'] = df_GS['pop'] * BASE_DATA_RATE_KBPS
    df_proxy_GS['traffic'] = df_proxy_GS['pop'] * BASE_DATA_RATE_KBPS

    traffic_metrics = dict()

    for ground_station in df_GS.itertuples(index=True, name='GroundStation'):

        # Sum of geodesic distance inverse from the source GS to all flights
        sum_all_geodesic_inverse_from_this_gs = sum([
            1/geodesic_distance_km(
                ground_station.lat, ground_station.lng,
                _flight.lat, _flight.lng
            ) for _flight in df_proxy_GS.itertuples(index=True, name='Flight')
        ])

        for flight in df_proxy_GS.itertuples(index=True, name='Flight'):

            # Sum of geodesic distance inverse from the source flight to all GSes
            sum_all_geodesic_inverse_from_this_flight = sum([
                1/geodesic_distance_km(
                    flight.lat, flight.lng,
                    _ground_station.lat, _ground_station.lng
                ) for _ground_station in df_GS.itertuples(index=True, name='GroundStation')
            ])

            geodesic_inverse = 1 / geodesic_distance_km(
                ground_station.lat, ground_station.lng,
                flight.lat, flight.lng
            )

            # Traffic metric for the source-destination pair in Gbps
            traffic_metrics[f'G-{ground_station.id}_F-{flight.id}'] = (
                (
                    ground_station.traffic *
                    (geodesic_inverse/sum_all_geodesic_inverse_from_this_gs)
                ) + (
                    flight.traffic *
                    (geodesic_inverse/sum_all_geodesic_inverse_from_this_flight)
                )
            )/1000000

    with open(TRAFFIC_MATRIX_JSON, 'w') as json_file:
        json_file.write(json.dumps(traffic_metrics, indent=2))


if __name__ == "__main__":

    # Input CSV file
    RAW_TM_GS_CSV = 'dataset/src/ground_stations/CSVs/preprocess/RAW_TM_GS_100.csv'
    FLIGHT_PROXY_GS_CSV = 'dataset/src/flights/dataset/flight_proxy_GS.csv'

    # Output JSON file
    TRAFFIC_MATRIX_JSON = 'traffic_matrix.json'

    BASE_DATA_RATE_KBPS = 300

    create_population_weighted_traffic_matrix()
