
'''
Fetches the ICAO codes of airlines from FlightRadar24 and saves them to a JSON file.
'''

import json

from FlightRadar24 import FlightRadar24API

AIRLINE_ICAO_JSON = 'dataset/src/flights/dataset/airline_ICAO_list.json'


flight_radar = FlightRadar24API()
airline_ICAO_list = [
    airline.get('ICAO')
    for airline in flight_radar.get_airlines()
]

with open(AIRLINE_ICAO_JSON, 'w') as json_file:
    json.dump(airline_ICAO_list, json_file)
