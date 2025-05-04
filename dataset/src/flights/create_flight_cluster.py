
'''
Create flight cluster based on the 10 degree of latitude and longitude air space 
and unique zonal tag, the number of passenger in each flight.
'''

import json

import pandas as pd

SEATING_CAPACITY = json.loads(open(
    'dataset/src/flights/dataset/max_passenger_capacity.json'
).read())

flight_coordinates = pd.read_csv(
    'dataset/src/flights/dataset/flight_on_air.csv'
).to_dict(orient='records')


for flight_coordinate in flight_coordinates:

    # Ignore if number of passenger less then 10
    if SEATING_CAPACITY[flight_coordinate.get('model_code')] < 10:
        continue

    flight_coordinate['passenger'] = SEATING_CAPACITY[
        flight_coordinate.get('model_code')
    ]

    # Building zonal tag based on lat/lng

    # Latitude code
    if flight_coordinate['lat']//10 < 0:
        lat_code = f'S{-1*int(int(flight_coordinate['lat'])//10)}'
    elif flight_coordinate['lat']//10 >= 0:
        lat_code = f'N{int(int(flight_coordinate['lat'])//10)}'

    # Longitude code
    if flight_coordinate['lng']//10 < 0:
        lng_code = f'W{-1*int(int(flight_coordinate['lng'])//10)}'
    elif flight_coordinate['lat']//10 >= 0:
        lng_code = f'E{int(int(flight_coordinate['lng'])//10)}'

    flight_coordinate['tag'] = f'{lat_code}{lng_code}'
    print(
        f'''|- ({flight_coordinate['lat']},{flight_coordinate['lng']}) : {flight_coordinate['tag']}'''
    )


df = pd.DataFrame.from_dict(flight_coordinates)
df.dropna(inplace=True)
df.to_csv(
    'dataset/src/flights/dataset/flight_cluster.csv',
    index=False
)
