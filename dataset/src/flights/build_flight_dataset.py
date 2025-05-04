
'''
Create a dataset of flights using FlightRadar24 API
'''

import csv
import json
import os
import random
import time

from FlightRadar24 import FlightRadar24API


def CSV_logger(data: dict):
    'Log data to a CSV file'

    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writeheader()

    with open(OUTPUT_CSV, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        writer.writerow(data)


def get_flights(airline: str) -> list | None:
    'Get flights for a given airline'

    try:
        flight_radar = FlightRadar24API()
        return flight_radar.get_flights(airline)

    except Exception:
        time.sleep(random.randint(5, 10))
        return None


def get_flight_details(flight) -> dict:
    'Get flight details for a given flight'

    try:
        flight_radar = FlightRadar24API()
        return flight_radar.get_flight_details(flight)

    except Exception:
        time.sleep(random.randint(5, 10))
        return None


if __name__ == '__main__':

    # Output CSV file path
    OUTPUT_CSV = 'dataset/src/flights/dataset/flight_dataset.csv'

    AIRLINES = json.loads(open(
        'dataset/src/flights/dataset/airline_ICAO_list.json'
    ).read())

    for idx, airline in enumerate(AIRLINES):

        # Get flights for the airline
        flights = get_flights(airline)
        while flights is None:
            print(f'|x [{idx+1}] {airline}')
            flights = get_flights(airline)

        for flight in flights:

            # Get flight details for the flight
            flight_details = get_flight_details(flight)
            while flight_details is None:
                print(f'|x [{idx+1}] {airline}')
                flight_details = get_flight_details(flight)

                # Check if the flight has a trail then record the data
                if flight_details.get("trail"):
                    CSV_logger({
                        'airline_name': flight_details["airline"]["name"],
                        'icao': flight_details["airline"]["code"]["icao"],
                        'model_code': flight_details["aircraft"]["model"]["code"],
                        'model_name': flight_details["aircraft"]["model"]["text"],
                        'registration': flight_details["aircraft"]["registration"],
                        'lat': flight_details["trail"][0]["lat"],
                        'lng': flight_details["trail"][0]["lng"],
                        'alt': flight_details["trail"][0]["alt"]
                    })

        print(f'|- [{idx+1}] {airline} -- total flights: {len(flights)} ')
