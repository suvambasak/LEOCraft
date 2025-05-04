
'''
This script extracts the model codes from the flight dataset and creates a JSON file
'''

import json

import pandas as pd

flights = pd.read_csv('dataset/src/flights/dataset/flight_dataset.csv')


maximum_passenger_capacity = dict()
for model_code in flights['model_code'].unique():
    maximum_passenger_capacity[model_code] = None


with open('dataset/src/flights/dataset/max_passenger_capacity.json', 'w') as json_file:
    json.dump(maximum_passenger_capacity, json_file, indent=4)
